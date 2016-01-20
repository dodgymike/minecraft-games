#!/usr/bin/python

import os,sys,time

stdin_slave, stdout_master = os.pipe()
stdin_master,stdout_slave  = os.pipe()

pid = os.fork()
if pid == 0:

    os.dup2(stdin_slave, 0)
#    os.dup2(stdout_slave, 1)
    cmd = ["./run_mc.sh","./run_mc.sh"]
    os.execv(cmd[0],cmd)

else:
    time.sleep(10)
    #while True:
    #    print os.read(stdin_master, 1)

    x_incr = 40
    y_incr = 20
    z_incr = 20

    x_max = 700
    x_min = 10
    y_max = 100
    y_min = 0
    z_max = 600
    z_min = 200

    x = x_min
    y = y_min
    z = z_min

    while True:
        if x >= x_max:
            x = x_min
            y += y_incr

        if y >= y_max:
            y = y_min
            z += z_incr

        if z >= z_max:
            print "done"
            break

        fill_string = "/fill {} {} {} {} {} {} air\n".format(x, y, z, x + x_incr, y + y_incr, z + z_incr)
        glass_fill_string = "/fill {} {} {} {} {} {} glass\n".format(x, y, z, x + x_incr, y, z + z_incr)
        tp_string = "/tp surfmike {} {} {}\n".format(x, y, z)
        print tp_string
        print fill_string
        os.write(stdout_master, tp_string)
        time.sleep(2)
        os.write(stdout_master, fill_string)
        time.sleep(2)

        if y == 0:
            print glass_fill_string
            os.write(stdout_master, glass_fill_string)
            time.sleep(1)

        x += x_incr
