import commands
import serial
import config
import plotty
from time import sleep
import time
import pandas as pd
from datetime import datetime
# station = 'Q'


class Error(Exception):
    """Base class for other exceptions"""
    pass


class portDisconnectError(Error):
    """Raised when b'' is detected."""
    pass


def resetElapsedTime():
    time_start = time.perf_counter()
    return(time_start)


def elapsedTime(x):
    time_elapsed = time.perf_counter() - x
    return(time_elapsed)


def serObj(url):
    return serial.serial_for_url(
        url=url,
        baudrate=config.baud_rate,
        do_not_open=True,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=1, timeout=config.tout)


def urlCreate(line):
    ipDict = config.ipConfig
    socketList = [5047, 5048]
    return ['socket://'+ipDict[line]+':'+str(i) for i in socketList]


def bytes_to_read(func):
    """[Specify the length of data to read]
    [return the list of data lengths for a given function]
    """
    return [commands.dataLen(i[2:4].decode()) for i in func]


def prepInit(station, selection):
    """Prepare intial commands up until checker commands"""
    z = commands.selection_TorS(station, selection)
    return zip(z, bytes_to_read(z))


def greetings(ser):
    """Catch greetings from console server"""
    for i in range(4):
        print(ser.readline())
    ser.reset_input_buffer()
    sleep(0.01)


def read_routine(ser, x, y):
    ser.write(x)
    sleep(0.01)
    readback = ser.read(y)
    if readback == b'':
        raise portDisconnectError
    print(readback)
    return readback


def fullSequence(chamber, url):
    """send all serial commands in sequence"""
    ser = serObj(url)
    result = {}
    station = commands.LUT(chamber)
    selection = 'speed'
    # for selection in ['speed']:
    dataList = []
    ser.open()
    # initiate connection
    greetings(ser)
    # read and write init serial commands
    for x, y in prepInit(station, selection):
        read_routine(ser, x, y)
    # start timer
    x = resetElapsedTime()
    # check speed 0
    ser.write(commands.checkerCmd(station))
    sleep(0.01)
    speed = ser.read(10)
    while speed[2:7] != b'A0000':
        ser.write(commands.checkerCmd(station))
        sleep(0.01)
        speed = ser.read(10)
        if(elapsedTime(x) >= config.max_duration):
            raise Exception("The carrier is not moving.")
            break
    # read and write middle commands
    for x, y in zip(commands.midCmd(station),
                    bytes_to_read(commands.midCmd(station))):
        read_routine(ser, x, y)
    # fetch data
    for x, y in zip(commands.fetchCmd(station),
                    bytes_to_read(commands.fetchCmd(station))):
        dataList.append(read_routine(ser, x, y).decode())
    # read and write ending commands
    for x, y in zip(commands.endCmd(station),
                    bytes_to_read(commands.endCmd(station))):
        read_routine(ser, x, y)
    ser.close()
    result['original'] = dataList
    return result


def mainDict(line):
    mainDict = {}
    urlList = urlCreate(line)
    first_chambers = commands.firstPort(line)
    second_chambers = commands.secondPort(line)
    for i, j in zip(urlList, (first_chambers, second_chambers)):
        mainDict[i] = j
    tempDict = {}
    for i in mainDict.keys():
        chamber_list = mainDict[i]
        for a in chamber_list:
            tempDict[a] = i
    return tempDict


# convert hexstring to signed decimal
def decodeOut(hexstr, bits):
    value = int(hexstr, 16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return(value)


def speedClean(B_array):
    firstPart = B_array[:-7]
    midPart = str(firstPart[7:])
    speed = midPart[:-4]
    speed_result = decodeOut(speed, config.decodeBits)
    return speed_result


def torqueClean(B_array):
    firstPart = B_array[:-7]
    midPart = str(firstPart[7:])
    torque = midPart[4:]
    torque_result = decodeOut(torque, config.decodeBits)/10
    return torque_result


def main():
    dateTime = datetime.now().strftime(config.pngdate)
    line = '203'
    temp = {'P1': 'socket://128.53.66.38:5047',
            'P2': 'socket://128.53.66.38:5047',
            'P3': 'socket://128.53.66.38:5047',
            'P4': 'socket://128.53.66.38:5047',
            'P5': 'socket://128.53.66.38:5047',
            'P6': 'socket://128.53.66.38:5047',
            'P7': 'socket://128.53.66.38:5047',
            'P8': 'socket://128.53.66.38:5047',
            'P9': 'socket://128.53.66.38:5047',
            'P10': 'socket://128.53.66.38:5047',
            'P11': 'socket://128.53.66.38:5047',
            'P12': 'socket://128.53.66.38:5047',
            'P13': 'socket://128.53.66.38:5047',
            'P14': 'socket://128.53.66.38:5047',
            'P15': 'socket://128.53.66.38:5047',
            'P16': 'socket://128.53.66.38:5047',
            'P17': 'socket://128.53.66.38:5047',
            'P18': 'socket://128.53.66.38:5047',
            'P19': 'socket://128.53.66.38:5047',
            'P20': 'socket://128.53.66.38:5047',
            'P21': 'socket://128.53.66.38:5047',
            'P22': 'socket://128.53.66.38:5047',
            'P23': 'socket://128.53.66.38:5047',
            'P24': 'socket://128.53.66.38:5047',
            'P25': 'socket://128.53.66.38:5047',
            'P26': 'socket://128.53.66.38:5047',
            'P27': 'socket://128.53.66.38:5047',
            'P28': 'socket://128.53.66.38:5047',
            'C2': 'socket://128.53.66.38:5047',
            'C3': 'socket://128.53.66.38:5047'}
    # temp = {'C3': 'socket://128.53.66.38:5047'}
    # temp = mainDict(line)
    # print(temp)
    for chamber, v in temp.items():
        try:
            print(f'{chamber}:{v}')
            dataDict = fullSequence(chamber, v)
            df = pd.DataFrame.from_dict(dataDict)
            df['Speed'] = df['original'].apply(lambda x: speedClean(x))
            df['Torque'] = df['original'].apply(lambda x: torqueClean(x))
            df = df.drop(['original'], axis=1)
            df.to_csv(f"{chamber}.csv", sep=';', index=True, mode='w')
            dfSpeed = df['Speed']
            dfTorque = df['Torque']
            # print(dfTorque.head(10))
            plotty.plot(line, chamber, dfSpeed, dfTorque, dateTime)
        except portDisconnectError as e:
            print(e)


if __name__ == '__main__':
    main()
