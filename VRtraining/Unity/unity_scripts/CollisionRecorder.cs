using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Text;



public class CollisionRecorder : MonoBehaviour
{

    public AudioSource music;
    public bool printN = false; //是否打印日志，
    public bool saveN = false; // 是否执行save操作
    public bool playAudioN = false; // 是否播放碰撞音效
    private Transform _transform;
    


    private void Awake()
    {
        music = GetComponent<AudioSource>();
        _transform = GetComponent<Transform>();
    }


    private void OnCollisionEnter(Collision collision)
    {
        string tag = collision.gameObject.tag;
        if (tag != "stair" && tag != "floor")
        {
            if (playAudioN)
            {
                playMusic();
            }
            if (printN)
            {
                Debug.Log("..Collision with " + tag + " in " + _transform.position.ToString());
            }
            appendLog("Collision with - " + tag + "-" + _transform.position.ToString("f6"));
        }
    }

    private string _logString;
    private void appendLog(string log)
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
            string logFileName = "CollisionLog-" + strNowTime + ".log";
            string logDirName = Application.dataPath + "/log";
            if (!Directory.Exists(logDirName))
            {
                Directory.CreateDirectory(logDirName);
            }
            string AbsoluteLogFileName = logDirName + "/" + logFileName;
            StreamWriter logWriter = new StreamWriter(AbsoluteLogFileName, false, System.Text.Encoding.Default);
            Debug.Log("======> CollisionLog saved at :" + AbsoluteLogFileName);
            logWriter.Write(_logString);
            logWriter.Close();//关闭流
        }

    }

    private void playMusic()//播放音效
    {
        if (music != null && !music.isPlaying)
        {
            music.Play();
        }
    }
}
