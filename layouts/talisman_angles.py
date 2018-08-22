import numpy as np
import pylab as pl

'''
240 pixels is less than 16*x16 grid = 256

we have 15 rings total:

 1   2   3   4   5   6   7   8   9  10  11 12 13  13 14 15
 1   2   1   2   1   2   1   2   1   2   1  2  1   2  2  2
29, 27, 25, 24, 22, 20, 18, 16, 14, 12, 10, 8, 2*, 6, 4, 3

const uint16_t Rings[9] = {0, 29, 29+25, 29+25+22, 29+25+22+18, 29+25+22+18+14, 29+25+22+18+14+10, 29+25+22+18+14+10+2}; 
    
const uint16_t Rings[10] = {0, 27, 27+24, 27+24+20, 27+24+20+16, 27+24+20+16+12, 27+24+20+16+12+8, 27+24+20+16+12+8+6, 27+24+20+16+12+8+6+4, 27+24+20+16+12+8+6+4+3}; 
 
 
Assume that each ring starts at 90 degrees (plus some tunable offset). Then can derive angle according to # of leds in ring and distance as a ratio of end of map to man. (because there are 15 rings)

From polar coords, can derive x, y of each led. The can rasterize onto 16x16 grid. Note that there are some grid cells which contain no LED (esp at outer edges). Thus, it location isn't splatted with some width, the person will not show up since there is no pixel to light up for them.  
 
 
====================================================

def loc_to_pixel(lat, lon):
    # I should have this in the processing code
    
    ...
    
    return pixel_x, pixel_y

def pixel_to_led_addr(pixel_x, pixel_y):

    # simplest would be to brute force search
    minD = 9999
    minD_idx = 0
    for chan, idx, x, y in led_addr_map:
        d = dist(pixel_x, pixel_y, x, y)
        if d < minD:
            minD = d
            minD_idx = chan*120 + idx
    return minD_idx//120, minD_idx%120
    
def set_leds_from_framebuffer(frame_r, frame_g, frame_b):
    #buf = ''
    for chan in [0, 1]:
        for idx in range(120):
            x, y = led_addr_map_x[chan][idx], led_addr_map_y[chan][idx] # in pixel coords
            r = frame_r[x][y];
            g = frame_g[x][y];
            b = frame_b[x][y];
            #buf += '%02x%02x%02x' % (r, g, b)
            leds[chan].SetPixelColor(idx, RgbColor(r,g,b));
'''

offsets =      [0,   0, -5, -5, -10,-10,-15,-15,-20,-20,-25,-25+10,-30-10,-30-45,-35, -35]
ringIdx =      [0,   1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 12,    13,  14]
chanIdx =      [1,   2,  1,  2,  1,  2,  1,  2,  1,  2,  1,  2,  1,  2,     2,   2]
numLedByChan = [29, 27, 25, 24, 22, 20, 18, 16, 14, 12, 10,  8,  2,  6,     4,   3]

betaLst = np.linspace(0, 0.75, 15)
numLedByRing = [29, 27, 25, 24, 22, 20, 18, 16, 14, 12, 10, 8, 8, 4, 3]

def return_angles(numLeds, offset=0):
    angles = [return_angle(x, numLeds, offset) for x in np.arange(numLeds)]
    return angles
    
def return_angle(ledNum, totalLedsInRing, offset=0):
    angleDiv = 360./totalLedsInRing
    startAngle = 90.0
    return (startAngle + offset + ledNum*angleDiv) % 360
     
def return_dist(ledNumOnRing, ringNum, ringDiv=1.0, beta=0.5):
    # 15 rings, but leave space in middle for man...
    # man is zero, so 0*ringDiv
    # first ring is 15*ringDiv
    # last ring is 1*ringDiv
    # now, to model spiral, 
    # we can interpolate between rings according to its pos
    alpha = 1.0*(ledNumOnRing)/(numLedByRing[ringNum]-1)
    dist1 = (15-ringNum)*ringDiv
    dist2 = (15-ringNum-1)*ringDiv
    return beta*((1-alpha)*dist1 + alpha*dist2) + (1-beta)*dist1

def to_cartesian(angle, d):
    return d*np.cos(angle), d*np.sin(angle)
    
if __name__ == '__main__':
    
    pts = [[],[]]
    
    ringDiv = 1.0
  
    for iter, (ring, chan, numLed) in enumerate(zip(ringIdx, chanIdx, numLedByChan)):
        print 'Ring %d, on chan %d' % (ring, chan)
        angles = [] #return_angles(numLed, offset=offsets[ring])
        dists = []
        for i in range(numLed):
            
            if ring == 12 and chan == 2:
                i_offset = 2
            else:
                i_offset = 0
            dists.append(return_dist(i+i_offset, ring, ringDiv=ringDiv, beta=betaLst[ring]))
            angles.append(return_angle(i+i_offset, numLedByRing[ring], offset=offsets[iter]))
        for angle, dist in zip(angles, dists):
            print angle, dist

            pts[chan-1].append([angle, dist])
 
    
    for chan in [1,2]:
        if chan == 1: color = 'red'
        else: color = 'blue'
                
        ptsChan = np.array(pts[chan-1])
        ax = pl.subplot(111, projection='polar')
        ax.plot(np.pi*ptsChan[:,0]/180.0, ptsChan[:,1], 's-', color=color, markersize=5)

    #ax.set_rmax(2)
    #ax.set_rticks([0.5, 1, 1.5, 2])  # less radial ticks
    ax.set_rlabel_position(-22.5)  # get radial labels away from plotted line
    ax.grid(True)
    
    of = open('talisman.json','w')
    of.write('[\n')
    for chan in [1, 2]:
        for i, pt in enumerate(pts[chan-1]):
            print chan, i, to_cartesian(pt[0]/180.0*np.pi, pt[1])
            x, y = to_cartesian(pt[0]/180.0*np.pi, pt[1])
            of.write('  {"point": [%f, 0.00, %f]},\n' % (x, y))
    of.write(']\n')     
    of.close()

    ax.set_title("Talisman LED Coordinates", va='bottom')
    pl.show()
    