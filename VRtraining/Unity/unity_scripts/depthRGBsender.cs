using UnityEngine;
using System.IO;
using System.Linq;
using System;
using System.Collections;
using UnityEngine.Networking;

public class depthRGBsender : MonoBehaviour
{

    private int factor_width = 10;
    private int factor_height = 10;
    private int width;
    private int height;
    private float[,] distance_shrink;
    private Texture2D screenShot;
    private string postUrl = "http://127.0.0.1:8311/local_nav";
    public bool sendN = false; //�Ƿ��͵�����Ϣ��������
    public bool useThis = false; //�Ƿ����øýű�
    public bool printFPS = false;
    private Camera cam; 

    private void calculateDistance(int start_width, int start_height, int end_width, int end_height, float[,] distance, int factor_width, int factor_height)
    {
        Ray ray;
        RaycastHit hit;
        Vector3 mousePosition;
        for (int i = start_width; i < end_width; i++)
        {
            for (int j = start_height; j < end_height; j++)
            {
                mousePosition = new Vector3(i * factor_width, j * factor_height, 0);
                ray = Camera.main.ScreenPointToRay(mousePosition);
                if (Physics.Raycast(ray, out hit))
                {
                    float temp_distance = (Camera.main.transform.position - hit.point).sqrMagnitude;
                    distance[i, j] = (float)Math.Round(temp_distance, 4);
                }
                else
                {
                    distance[i, j] = 0;
                }
            }
        }
    }

    private void printScreenInformation()
    {
        print("Screen Resolution: " + Screen.width + "x" + Screen.height); 
        print("Downscale Factor: (" + factor_width + "," + factor_height + ")");
        width = Screen.width / factor_width;
        height = Screen.height / factor_height;
        print("Result Resolution: " + width + "x" + height);
        distance_shrink = new float[width, height];
    }

    void Start()
    {
        cam = GameObject.Find("CameraForScreenshot").GetComponent<Camera>();
        Debug.Log("���+RGB�ɼ��Ƿ�������" + useThis + " �Ƿ�ɼ������ͣ�" + sendN);
        screenShot = new Texture2D(cam.targetTexture.width, cam.targetTexture.height, TextureFormat.RGB24, false);
        printScreenInformation();

    }

    void main()
    {

        calculateDistance(0, 0, width, height, distance_shrink, factor_width, factor_height);
        StartCoroutine(SendOnce());
    }


    IEnumerator SendOnce()
    {
/*        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = cam.targetTexture;
        screenShot.ReadPixels(new Rect(0, 0, cam.targetTexture.width, cam.targetTexture.height), 0, 0, false);
        RenderTexture.active = currentRT;
        byte[] bytes = screenShot.EncodeToPNG();*/
        ////byte[] bytes = null;
        String s1 = String.Join(",", distance_shrink.Cast<float>());
        WWWForm form = new WWWForm();
        form.AddField("depth_frame", s1);
        // form.AddBinaryData("rgb", bytes, "imagedata.raw");
        UnityWebRequest request = UnityWebRequest.Post(postUrl, form);
        yield return request.SendWebRequest();



    }

    // Update is called once per frame
    void Update()
    {
        if (useThis)
        {
            if (sendN)
            {
                main();
            }
        }


    }

    //��ӡ֡��
    private void OnGUI()
    {
        if (printFPS)
        {
            GUI.contentColor = Color.red;
            GUI.Label(new Rect(10, 10, 100, 30), ((int)(1.0f / Time.smoothDeltaTime)).ToString());
            GUI.skin.label.fontSize = 22;
        }

    }
}
