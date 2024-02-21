using UnityEngine;
using System.IO;
using System.Linq;
using System;
using System.Collections;
using UnityEngine.Networking;

public class RGBsender : MonoBehaviour
{
    private int factor_width = 5;
    private int factor_height = 5;
    private int count = 0;
    public uint sampleFrequence { get; private set; } = 50;
    private int width;
    private int height;
    private Texture2D screenShot;
    //private string postUrl = "http://192.168.0.105:8211/userInterface"; 
    private string postUrl = "http://127.0.0.1:8411/userInterface"; 
    public bool sendN = false; //是否发送导航信息到服务器
    public bool useThis = false; //是否启用该脚本
    private Camera cam; 

    public static string GetTimeStamp()
    {
        TimeSpan ts = DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, 0);
        return Convert.ToInt64(ts.TotalMilliseconds).ToString();
    }

void Awake()
    {
        cam = GameObject.Find("CameraForScreenshot").GetComponent<Camera>();
        screenShot = new Texture2D(cam.targetTexture.width, cam.targetTexture.height, TextureFormat.RGB24, false);

    }

    void main()
    {
        StartCoroutine(SendOnce());
    }


    IEnumerator SendOnce()
    {
        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = cam.targetTexture;
        screenShot.ReadPixels(new Rect(0, 0, cam.targetTexture.width, cam.targetTexture.height), 0, 0, false);
        RenderTexture.active = currentRT;
        byte[] bytes = screenShot.EncodeToPNG();
        WWWForm form = new WWWForm();
        form.AddBinaryData("rgb", bytes, "imagedata.raw");
        UnityWebRequest request = UnityWebRequest.Post(postUrl, form);
        yield return request.SendWebRequest();
    }


    void FixedUpdate()
    {
        if (useThis)
        {
            if (sendN)
            {
                string strNowTime = GetTimeStamp();
                string str_y = transform.eulerAngles.y.ToString();
                //print("current yaw of player is ......." + strNowTime + "<==！！！==>" + str_y);
                count += 1;
                if (count % sampleFrequence == 0)
                {
                    main();
                }

            }
        }


    }

}
