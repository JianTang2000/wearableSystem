using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.UIElements;


public class PathLogger : MonoBehaviour
{
    private string _logString;
    public void appendLog(string log)
    {
        DateTime dateTime = DateTime.Now;
        string strNowTime = string.Format("[{0:D}{1:D}{2:D}{3:D}{4:D}{5:D}]",
            dateTime.Year, dateTime.Month, dateTime.Day, dateTime.Hour, dateTime.Minute, dateTime.Second);
        _logString += strNowTime + ' ' + log;
        _logString += '\n';
    }
    private void OnDestroy()
    {
        DateTime dateTime = DateTime.Now;
        string strNowTime = string.Format("{0:D}{1:D}{2:D}{3:D}{4:D}{5:D}",
            dateTime.Year, dateTime.Month, dateTime.Day, dateTime.Hour, dateTime.Minute, dateTime.Second);
/*        string logFileName = strNowTime + "-Path.log";
        string logDirName = Application.dataPath + "/log";
        if (!Directory.Exists(logDirName))
        {
            Directory.CreateDirectory(logDirName);
        }
        string AbsoluteLogFileName = logDirName + "/" + logFileName;
        StreamWriter logWriter = new StreamWriter(AbsoluteLogFileName, false, System.Text.Encoding.Default);
        logWriter.Write(_logString);*/
    }
}
