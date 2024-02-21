using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;



public class QuaternionTest : MonoBehaviour
{
    private string postUrl = "http://192.168.0.101:8211/userInterface";

    private const string player_position = "player_position";
    private const string steering_target = "steering_target";
    private const string player_rotation_y = "player_rotation_y";

    private void Start()
    {
        StartCoroutine(SendOnce());
    }


    IEnumerator SendOnce()
    {
        WWWForm form = new WWWForm();
        form.AddField(player_position, "(-7.8, 1.0, 4.0)");
        form.AddField(steering_target, "(-0.7, 1.0, 2.3)");
        form.AddField(player_rotation_y, "39.24004");

        UnityWebRequest request = UnityWebRequest.Post(postUrl, form);
        yield return request.SendWebRequest();
        if (request.isHttpError || request.isNetworkError)
        {
            Debug.LogError("*************请求服务器发生错误*************");
            Debug.LogError(request.error);
        }
        else
        {
            Debug.Log("请求服务器 OK ");
        }
    }
}