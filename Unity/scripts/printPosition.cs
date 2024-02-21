using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Text;
using UnityEngine.Networking;
using UnityEngine.UI;
using UnityEngine.AI;
using UnityEditor;





public class printPosition : MonoBehaviour
{

    public bool runTurnExp = false;

    // 降低采样频率
    public uint sampleFrequence { get; private set; } = 1;
    private uint count = 0;


    void Start()
    {
        Debug.Log("======>当前object--" + transform.tag + "--的全局坐标 is " + transform.position);
    }

    void Update()
    {
        if (runTurnExp)
        {
            count += 1;
            if (count % sampleFrequence == 0)
            {
                appendLog("player yaw = " + transform.eulerAngles.y);
                //Debug.Log("======>当前object--" + transform.tag + "--的yaw is " + transform.eulerAngles.y);
            }
        }
        
    }

    public static string GetTimeStamp()
    {
        TimeSpan ts = DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, 0);
        return Convert.ToInt64(ts.TotalMilliseconds).ToString();
    }

    private string _logString;
    private void appendLog(string log)
    {
        string strNowTime = GetTimeStamp();
        _logString += strNowTime + '-' + log;
        _logString += '\n';
    }

    // 最后结束后，可能_logString还有一部分没有达到存的条件，所以在退出时进行保存
    private void OnDestroy()
    {
        if (runTurnExp)
        {
            DateTime dateTime = DateTime.Now;
            string strNowTime = string.Format("{0:D}{1:D}{2:D}{3:D}{4:D}{5:D}",
                dateTime.Year, dateTime.Month, dateTime.Day, dateTime.Hour, dateTime.Minute, dateTime.Second);
            string logFileName = "turn-in-space-exp-log-" + strNowTime + ".log"; 
            string logDirName = Application.dataPath + "/log";
            if (!Directory.Exists(logDirName))
            {
                Directory.CreateDirectory(logDirName);
            }
            string AbsoluteLogFileName = logDirName + "/" + logFileName;
            StreamWriter logWriter = new StreamWriter(AbsoluteLogFileName, false, System.Text.Encoding.Default);
            Debug.Log("......log saved at :" + AbsoluteLogFileName);
            logWriter.Write(_logString);
            logWriter.Close();//关闭流
        }
    }


}
