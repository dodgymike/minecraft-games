#!/usr/bin/python

import json
import os,sys,time

stdin_slave, stdout_master = os.pipe()
stdin_master,stdout_slave  = os.pipe()

def save_config(config):
    with open('config.json', 'w') as outfile:
        json.dump(config, outfile)

def load_config():
    with open('config.json', 'r') as infile:
        return json.load(infile)

pid = os.fork()
if pid == 0:

    os.dup2(stdin_slave, 0)
#    os.dup2(stdout_slave, 1)
    cmd = ["./run_mc.sh","./run_mc.sh"]
    os.execv(cmd[0],cmd)

else:
    time.sleep(30)
    #while True:
    #    print os.read(stdin_master, 1)

    config = load_config()

    x_incr = 40
    y_incr = 20
    z_incr = 20

    x_max = 700
    x_min = -100
    y_max = 100
    y_min = 0
    z_max = 600
    z_min = 240

    x = x_min
    y = y_min
    z = z_min

    spawn_x = 1
    spawn_height = 60
    spawn_y = 1
    lava_depth = 1
    lava_level = 1
    interval = 5

    if "spawn_x" in config:
      spawn_x = config["spawn_x"]
    if "spawn_y" in config:
      spawn_y = config["spawn_y"]
    if "spawn_height" in config:
      spawn_height = config["spawn_height"]
    if "lava_depth" in config:
      lava_depth = config["lava_depth"]
    if "lava_level" in config:
      lava_level = config["lava_level"]
    if "interval" in config:
      interval = config["interval"]

    print("spawn_x ({})".format(spawn_x))
    print("spawn_y ({})".format(spawn_y))
    print("spawn_height ({})".format(spawn_height))
    print("lava_depth ({})".format(lava_depth))
    print("lava_level ({})".format(lava_level))
    print("interval ({})".format(interval))

    save_config({
      "spawn_x" : spawn_x,
      "spawn_y" : spawn_y,
      "spawn_height": spawn_height,
      "lava_depth": lava_depth,
      "lava_level": lava_level,
      "interval": interval,
    })

    # always set world spawn point
    os.write(stdout_master, "/difficulty peaceful\n")
    time.sleep(0.5)
    os.write(stdout_master, "/setworldspawn {} {} {}\n".format(spawn_x, spawn_height ,spawn_y))
    time.sleep(0.5)
    os.write(stdout_master, "/worldborder center 0 0\n")
    time.sleep(0.5)
    os.write(stdout_master, "/worldborder set 50\n")
    time.sleep(0.5)
    os.write(stdout_master, "/op surfmike\n")
    time.sleep(0.5)

    #for height in range(1, spawn_height):
    #  os.write(stdout_master, "/fill -25 {} -25 25 {} 25 cobblestone\n".format(height, height+1))
    #  time.sleep(1)
    #for height in range(spawn_height, spawn_height+5):
    #  os.write(stdout_master, "/fill -25 {} -25 25 {} 25 air\n".format(height, height+1))
    #  time.sleep(1)
    #os.write(stdout_master, "/fill -25 {} -25 25 {} 25 oak_planks\n".format(spawn_height, spawn_height-5))
    #time.sleep(1)

    while True:
      os.write(stdout_master, "/worldborder center {} {}\n".format(spawn_x, spawn_y))

      while True:
        os.write(stdout_master, "/say Remember kids, lava is the floor\n")

        time_left = 30
        while time_left > 0:
            os.write(stdout_master, "/say {} seconds left until lava goes up\n".format(time_left))
            time_left -= interval
            time.sleep(interval)

        os.write(stdout_master, "/fill {} {} {} {} {} {} lava keep\n".format(spawn_x-25, lava_level-lava_depth, spawn_y-25, spawn_x + 25, lava_level, spawn_y + 25))
        time.sleep(0.5)
        os.write(stdout_master, "/fill {} {} {} {} {} {} glass hollow\n".format(spawn_x-5, lava_level+5, spawn_y-5, spawn_x+5, lava_level+15, spawn_y+5))
        time.sleep(0.5)
        os.write(stdout_master, "/fill {} {} {} {} {} {} cobblestone\n".format(spawn_x+3, lava_level+5, spawn_y+3, spawn_x+1, lava_level+6, spawn_y+1))
        time.sleep(0.5)
        os.write(stdout_master, "/fill {} {} {} {} {} {} oak_planks\n".format(spawn_x-25, 1, spawn_y-25, spawn_x-25, 255, spawn_y-25))
        time.sleep(0.5)
        os.write(stdout_master, "/fill {} {} {} {} {} {} oak_planks\n".format(spawn_x+4, lava_level+5, spawn_y+4, spawn_x+5, lava_level+6, spawn_y+5))
        time.sleep(0.5)
        os.write(stdout_master, "/fill {} {} {} {} {} {} iron_ore\n".format(spawn_x-4, lava_level+5, spawn_y-4, spawn_x-5, lava_level+6, spawn_y-5))
        time.sleep(0.5)
        os.write(stdout_master, "/fill {} {} {} {} {} {} coal_ore\n".format(spawn_x-4, lava_level+5, spawn_y+4, spawn_x-5, lava_level+6, spawn_y+5))
        time.sleep(0.5)
        os.write(stdout_master, "/setworldspawn {} {} {}\n".format(spawn_x, lava_level+6, spawn_y))
        time.sleep(0.5)
        lava_level += lava_depth
        config["lava_level"] = lava_level
        save_config({
          "spawn_x" : spawn_x,
          "spawn_y" : spawn_y,
          "spawn_height": spawn_height,
          "lava_depth": lava_depth,
          "lava_level": lava_level,
          "interval": interval,
        })

        if lava_level >= 255:
          os.write(stdout_master, "/say GAME OVER\n")
          break

      spawn_x += 150
      if spawn_x > 1000:
        spawn_x = 1
        spawn_y += 150

      lava_level = 1
      save_config({
        "spawn_x" : spawn_x,
        "spawn_y" : spawn_y,
        "spawn_height": spawn_height,
        "lava_depth": lava_depth,
        "lava_level": lava_level,
        "interval": interval,
      })
