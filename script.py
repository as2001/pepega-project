import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):
    name = 'name'
    num_frames = 1
    shading = 'flat'
    hasf = False
    hasv = False
    is_anim = False
    for command in commands:
        if command['op'] == 'frames':
            is_anim = True
            hasf = True
            num_frames = int(command['args'][0])
        if command['op'] == 'basename':
            name = command['args'][0]
        if command['op'] == 'vary':
            hasv = True
        if command['op'] == 'shading':
            shading = command['shade_type']
    if hasv and not hasf:
        exit()
    return (name, num_frames, shading, is_anim)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob'sz
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(int(num_frames)) ]
    for command in commands:
        op = command["op"]
        if op == "vary":
            knob = command["knob"]
            args = command["args"]
            start_frame,end_frame = int(args[0]),int(args[1])
            start_value,end_value = args[2],args[3]
            n = 0
            for i, fram in enumerate(frames):
                if i in range(start_frame,end_frame+1):
                    f = end_frame - start_frame
                    step = (end_value - start_value)/f
                    frames[i][knob] = start_value + n*step
                    n += 1;
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]

    symbols['.def_light'] = ['light',
                            {'color' : [255, 255, 255],
                             'location': [0.5, 0.75, 1]}]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    light = '.def_light'
    reflect = '.white'

    (name, num_frames, shading, is_anim) = first_pass(commands)
    frames = second_pass(commands, num_frames)

    tmp = new_matrix()
    ident( tmp )
    
    step_3d = 100
    consts = ''
    coords = []
    coords1 = []

    for i, frame in enumerate(frames):
        tmp = new_matrix()
        ident(tmp)
        stack = [[x[:] for x in tmp]]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        lights = []
        for command in commands:   
            c = command['op']
            args = command['args']
            knob = 1
            if c == 'box':
                if not lights:
                    lights.append(light)
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, lights, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if not lights:
                    lights.append(light)
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, lights, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if not lights:
                    lights.append(light)
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, lights, symbols, reflect, shading)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'light':
                lights.append(command['light'])
            elif c == 'ambient':
                ambient = args
            elif c == 'move':
                if command["knob"]:
                    knob = frames[i][command["knob"]]                
                tmp = make_translate(args[0]*knob, args[1]*knob,args[2]*knob)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if command["knob"]:
                    knob = frames[i][command["knob"]]
                tmp = make_scale(args[0]*knob, args[1]*knob, args[2]*knob)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if command["knob"]:
                    knob = frames[i][command["knob"]]
                theta *= knob
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen,args[0])
                    
        if is_anim:
            num = format(i, "03")
            print(num)
            save_extension(screen, "anim/" + name + num)

    if is_anim:
        try:
            make_animation(name)
        except:
            print('Failed')

    
