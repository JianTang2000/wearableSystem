using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using Unity.Collections;
using UnityEngine;
using System.Text;


public class trajectoryRecoder : MonoBehaviour
{
    private uint count = 0;
    public uint sampleFrequence { get; private set; } = 5;
    public bool saveN = false;

    // Start is called before the first frame update
    void Start()
    {
        Debug.Log("Trajectory recording script has started... Would you like to save the trajectory data to a file?" + saveN);
    }

    // Update is called once per frame
    void Update()
    {
        count += 1;
        if (count % sampleFrequence == 0)
        {
            string new_log = transform.position.ToString("#0.0000");
            Savepath(new_log);
        }
    }

    private string _logString;
    private void Savepath(string log)
    {
        DateTime dateTime = DateTime.Now;
        string strNowTime = string.Format("[{0:D}{1:D}{2:D}{3:D}{4:D}{5:D}]",
            dateTime.Year, dateTime.Month, dateTime.Day, dateTime.Hour, dateTime.Minute, dateTime.Second);
        _logString += strNowTime + '-' + log;
        _logString += '\n';

    }

    private void OnDestroy()
    {
        if (saveN)
        {
            DateTime dateTime = DateTime.Now;
            string strNowTime = string.Format("{0:D}{1:D}{2:D}{3:D}{4:D}{5:D}",
                dateTime.Year, dateTime.Month, dateTime.Day, dateTime.Hour, dateTime.Minute, dateTime.Second);
            string logFileName = "TrajectoryLog-" + strNowTime + ".log";
            string logDirName = Application.dataPath + "/log";
            if (!Directory.Exists(logDirName))
            {
                Directory.CreateDirectory(logDirName);
            }
            string AbsoluteLogFileName = logDirName + "/" + logFileName;
            StreamWriter logWriter = new StreamWriter(AbsoluteLogFileName, false, System.Text.Encoding.Default);
            Debug.Log("......Trajectory log saved at :" + AbsoluteLogFileName);
            logWriter.Write(_logString);
            logWriter.Close();
        }

    }

}
