#!/usr/bin/python

import json
import os,sys,time
import select

stdin_slave, stdout_master = os.pipe()
stdin_master,stdout_slave  = os.pipe()

def save_config(config):
    with open('config.json', 'w') as outfile:
        json.dump(config, outfile)

def load_config():
    with open('config.json', 'r') as infile:
        return json.load(infile)

def send_command(command_text):
    os.write(stdout_master, str.encode("{}\n".format(command_text)))
    print("COMMAND: {}".format(command_text))
    time.sleep(0.5)

def chars_to_read():
  poll = select.poll()
  poll.register(stdin_master, select.POLLIN | select.POLLPRI)
  fd = poll.poll(0.5)
  if len(fd):
    f = fd[0]
    if f[1] > 0:
      return True

  return False

def print_all():
    while chars_to_read():
      print(read_response())

def read_all():
    responses = []
    while chars_to_read():
      responses.append(read_response())
 
    return responses

def read_response():
    if not chars_to_read():
      return None

    response = b''

    while True:
      response_char = os.read(stdin_master, 1)
      #print(response_char)
      if response_char == b'\n':
        #print("NEW RESPONSE LINE")
        return response.decode("utf-8")
         
      response += response_char

def has_players():
    print_all()

    send_command("/list")

    list_responses = read_all()

    for response in list_responses:
        print("Player list response ({})".format(response))
        if "There are 0 of a max " in response:
            return False

    return True

pid = os.fork()
if pid == 0:

    os.dup2(stdin_slave, 0)
    os.dup2(stdout_slave, 1)
    cmd = ["./run_mc.sh","./run_mc.sh"]
    os.execv(cmd[0],cmd)

else:
    print("Waiting for server to finish startup")
    while True:
      response = read_response()
      print("Got response ({})".format(response))
      if response == None:
        time.sleep(1)
        continue

      print("Got response ({})".format(response))
      if "INFO]: Done" in response:
        print("Server startup complete")
        break

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

    while not has_players():
        print("No Players")
        time.sleep(10)

    # always set world spawn point
    send_command("/gamemode survival @a")
    send_command("/difficulty peaceful")
    send_command("/setworldspawn {} {} {}".format(spawn_x, spawn_height ,spawn_y))
    send_command("/worldborder center 0 0")
    send_command("/worldborder set 50")
    send_command("/op surfmike")

    print_all()

    #for height in range(1, spawn_height):
    #  send_command("/fill -25 {} -25 25 {} 25 cobblestone".format(height, height+1))
    #  time.sleep(1)
    #for height in range(spawn_height, spawn_height+5):
    #  send_command("/fill -25 {} -25 25 {} 25 air".format(height, height+1))
    #  time.sleep(1)
    #send_command("/fill -25 {} -25 25 {} 25 oak_planks".format(spawn_height, spawn_height-5))
    #time.sleep(1)

    while True:
      if not has_players():
          print("No Players")
          time.sleep(10)
          continue

      send_command("/worldborder center {} {}".format(spawn_x, spawn_y))
      print_all()

      while True:
        send_command("/say Remember kids, lava is the floor")
        print_all()

        time_left = 30
        while time_left > 0:
            send_command("/say {} seconds left until lava goes up".format(time_left))
            time_left -= interval
            time.sleep(interval)

        send_command("/fill {} {} {} {} {} {} lava keep".format(spawn_x-25, lava_level-lava_depth, spawn_y-25, spawn_x + 25, lava_level, spawn_y + 25))
        time.sleep(0.5)
        send_command("/fill {} {} {} {} {} {} glass hollow".format(spawn_x-5, lava_level+5, spawn_y-5, spawn_x+5, lava_level+15, spawn_y+5))
        time.sleep(0.5)
        send_command("/fill {} {} {} {} {} {} cobblestone".format(spawn_x+3, lava_level+5, spawn_y+3, spawn_x+1, lava_level+6, spawn_y+1))
        time.sleep(0.5)
        send_command("/fill {} {} {} {} {} {} oak_planks".format(spawn_x-25, 1, spawn_y-25, spawn_x-25, 255, spawn_y-25))
        time.sleep(0.5)
        send_command("/fill {} {} {} {} {} {} oak_planks".format(spawn_x+4, lava_level+5, spawn_y+4, spawn_x+5, lava_level+6, spawn_y+5))
        time.sleep(0.5)
        send_command("/fill {} {} {} {} {} {} iron_ore".format(spawn_x-4, lava_level+5, spawn_y-4, spawn_x-5, lava_level+6, spawn_y-5))
        time.sleep(0.5)
        send_command("/fill {} {} {} {} {} {} coal_ore".format(spawn_x-4, lava_level+5, spawn_y+4, spawn_x-5, lava_level+6, spawn_y+5))
        time.sleep(0.5)
        send_command("/setworldspawn {} {} {}".format(spawn_x, lava_level+6, spawn_y))
        time.sleep(0.5)
        print_all()

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
          send_command("/say GAME OVER")
          break

        if not has_players():
            print("No Players")
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
