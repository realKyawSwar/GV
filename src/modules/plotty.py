import matplotlib.pyplot as plt
import numpy as np
import os
# from showa.modules import config
import config
from scipy.integrate import trapz
# from showa.lib import logs
from datetime import datetime
from pathlib import Path

if config.picPath == "":
    here = Path(__file__).resolve().parents[3]
    fileLocation = str(here) + "/data/"
else:
    fileLocation = config.picPath


def newDir(dateTime, lineNo):
    dirName = fileLocation + "/" + lineNo + "/" + dateTime
    # Create target directory & all intermediate directories if don't exists
    try:
        os.makedirs(dirName)
        print("Directory ", dirName,  " Created ")
        # logs.logInfo("Directory for L{} is created".format(lineNo))
    except FileExistsError:
        # print("Directory ", dirName,  " already exists")
        pass

    # Create target directory & all intermediate directories if don't exists
    if not os.path.exists(dirName):
        os.makedirs(dirName)
        # print("Directory ", dirName,  " Created hor ")
    else:
        print("Directory Okay")
    return(dirName)


def picName(comport, lineNo):
    dt_string = datetime.now().strftime(config.pngdate)
    # dateTime = datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
    picName = lineNo + "_" + comport + "_" + dt_string
    return(picName)


def picTitle(comport, lineNo):
    dt_string2 = datetime.now().strftime(config.dateonGraph)
    picTitle = lineNo + " " + comport + " " + dt_string2
    return(picTitle)


def status(dfTorque):
    x = config.controlLine
    y = config.controlLine*(-1)
    tmax = dfTorque.max()
    # print(tmax)
    tmin = dfTorque.min()
    # print(tmin)
    if tmax > x or tmin < y:
        status = 'Abnormal Torque Peak detected.'
    else:
        status = 'Normal'
    return (status)


def plot(lineNo, chamber, dfSpeed, dfTorque, dateTime):
    try:
        # dfTorque = df['Torque']
        # dfSpeed = df['Speed']
        img = plt.imread("bg.jpg")
        fig, ax1 = plt.subplots(facecolor=config.facecolor, figsize=(13, 9))
        ax2 = ax1.twinx()
        ax1.plot(dfTorque.index, dfTorque, '{}-'.format(config.torquecolor))
        ax1.plot([0, 1023], [config.controlLine, config.controlLine], 'c--')
        ax1.plot([0, 1023], [config.controlLine*(-1), config.controlLine*(-1)],
                 'c--')
        # ax1.plot([80, 80], [config.controlLine*(-1), config.controlLine], 'c*')
        # ax1.plot([140, 140], [config.controlLine*(-1), config.controlLine], 'c*')
        ax2.plot(dfSpeed.index, dfSpeed, '{}-'.format(config.speedcolor))
        # Specify background color for the axis/plot
        ax1.imshow(img, extent=[0, 1023, -600, 600])
        ax1.set_facecolor("black")
        ax1.set_xticks(np.arange(0, 1024, 50))
        ax1.set_yticks(np.arange(-3000, 3000, 50))
        ax1.tick_params(axis='y', colors=config.torquecolor)
        ax2.tick_params(axis='y', colors=config.speedcolor)
        ax1.set_ylim((-100, 100))
        ax1.set_xlim((0, 240))
        ax1.set_clip_on(False)
        ax2.set_ylim((-3200, 3200))
        ax2.set_xlim((0, 1023))
        # fig.suptitle()
        temp = status(dfTorque)
        if temp == 'Normal':
            ax1.set_title(temp, color='green')
        else:
            ax1.set_title(temp, color='red')
        ax1.set_xlabel('{}'.format(picTitle(chamber, lineNo)), fontsize=14,
                       fontweight='bold')
        ax1.set_ylabel('Torque', color=config.torquecolor)
        ax2.set_ylabel('Speed', color=config.speedcolor)
        ax1.grid(linestyle='-', linewidth='0.5', color=config.gridcolor)
        # print(fileLocation)
        # annotation of highest torque
        dfTorque = dfTorque.reset_index()
        tmax = dfTorque['Torque'].max()
        xindex = dfTorque.query('Torque == {}'.format(tmax))['index']
        xmax = xindex.iat[0]
        tmin = dfTorque['Torque'].min()
        xxindex = dfTorque.query('Torque == {}'.format(tmin))['index']
        xmin = xxindex.iat[0]
        bbox_props = dict(boxstyle="round,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops = dict(arrowstyle="->",
                          connectionstyle="angle,angleA=0,angleB=60",
                          color="white")
        kw = dict(xycoords='data', textcoords="axes fraction",
                  arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
        ax1.annotate('{}'.format(round(tmax, 1)), xy=(xmax, tmax),
                     xytext=(0.98, 0.98), **kw)
        ax1.annotate('{}'.format(round(tmin, 1)), xy=(xmin, tmin),
                     xytext=(0.05, 0.05), **kw)
        plt.tight_layout()
        fig.savefig("{}/{}.png".format(newDir(dateTime, lineNo),
                    picName(chamber, lineNo)), facecolor=fig.get_facecolor(),
                    transparent=True)
    except Exception as e:
        print("Error encountered during plotting.{}".format(e))
