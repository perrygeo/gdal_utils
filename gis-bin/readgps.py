import gps, os, time

session = gps.gps()

while 1:
    os.system('clear')
    session.query('admosy')
    # a = altitude, d = date/time, m=mode,
    # o=postion/fix, s=status, y=satellites

    print
    print ' GPS reading'
    print '----------------------------------------'
    print 'latitude    ' , session.fix.latitude
    print 'longitude   ' , session.fix.longitude
    print 'time utc    ' , session.utc, session.fix.time
    print 'altitude    ' , session.fix.altitude
    print 'eph         ' , session.fix.eph
    print 'epv         ' , session.fix.epv
    print 'ept         ' , session.fix.ept
    print 'speed       ' , session.fix.speed
    print 'climb       ' , session.fix.climb

    print
    print ' Satellites (total of', len(session.satellites) , ' in view)'
    for i in session.satellites:
        print '\t', i

    time.sleep(3)
