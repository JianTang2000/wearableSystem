using System.Collections;
using UnityEngine.Networking;
using UnityEngine;
using System.Collections.Generic;
using UnityEngine.UI;
using UnityEngine.AI;
using UnityEditor;
using System;



public class CoinNav : MonoBehaviour
{
    private uint count = 0;
    public uint sampleFrequence { get; private set; } = 10; 
    private string postUrl = "http://127.0.0.1:8211/userInterface"; 


    public bool useThis = false; 
    public bool sendN = false; 
    public bool printN = false; 
    private bool notDraw = true; 
    private NavMeshPath pathStart;
    public GameObject target; //选一个目标，需要是walkable属性
    private NavMeshAgent agent; //给绑定的object添加 nav agnet组件
    private const string player_position = "player_position";
    private const string steering_target = "steering_target";
    private const string player_rotation_y = "player_rotation_y";
    private const string remaining_distance = "remaining_distance";
    private const string corners_length = "corners_length";
    private const string direciton_name = "direction";

    private void Awake()//第一次调用，初始化文件
    {
        agent = GetComponent<NavMeshAgent>();//调用组件
        //禁用旋转，不然agent会（在调用了agent.steeringTarget之后？）自己转到该转的方向 
        agent.updateRotation = false;
    }

    IEnumerator SendOnce(string s1, string s2, string s3, string s4, string s5, string s6)
    {
        WWWForm form = new WWWForm();
        form.AddField(player_position, s1);
        form.AddField(steering_target, s2);
        form.AddField(player_rotation_y, s3);
        form.AddField(remaining_distance, s4);
        form.AddField(corners_length, s5);
        form.AddField(direciton_name, s6);

        UnityWebRequest request = UnityWebRequest.Post(postUrl, form);
        yield return request.SendWebRequest();
        if (printN) // 选择是否打印日志
        {
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


    private float GetPathRemainingDistance()
    {
        if (agent.pathPending ||
            agent.pathStatus == NavMeshPathStatus.PathInvalid ||
            agent.path.corners.Length == 0)
            return -1f;

        float distance = 0.0f;
        for (int i = 0; i < agent.path.corners.Length - 1; ++i)
        {
            distance += Vector3.Distance(agent.path.corners[i], agent.path.corners[i + 1]);
        }

        return distance;
    }

    float rotationAngle(Transform transform, Vector3 target)
    {
        GameObject tempObject = new GameObject();
        tempObject.transform.position = transform.position;
        Vector3 tempDirection = transform.eulerAngles;
        //Debug.Log("Initila Angle: " + tempDirection);
        tempObject.transform.LookAt(target);
        //Debug.Log("Final Angle: " + tempObject.transform.eulerAngles);
        //Debug.Log("Rotation Angle: " + (tempObject.transform.eulerAngles - tempDirection));
        float result = (tempObject.transform.eulerAngles - tempDirection).y;
        DestroyImmediate(tempObject);
        return (result + 360) % 360;
    }


    string retrieveDirection()
    {
        string result;
        float angle = rotationAngle(transform, agent.steeringTarget);
        //print(angle);
        //if (angle < 0 || angle >= 360) throw new Exception();
        if (angle <= 180)
        {
            result = angle + " right";
        }
        else
        {
            result = 360 - angle + " left";
        }
        return result;
    }


    private void FixedUpdate()
    {
        if (useThis)
        {

            agent.SetDestination(target.transform.position);
            agent.isStopped = true; //不允许导航算法自动驱动player移动

            if (!notDraw)
            {

                for (int i = 0; i < pathStart.corners.Length - 1; i++)
                    Debug.DrawLine(pathStart.corners[i], pathStart.corners[i + 1], Color.red);

            }



            count += 1;
            if (count % sampleFrequence == 0 && agent.hasPath)
            {

                float distance = GetPathRemainingDistance();
                Vector3 c_position = transform.position;
                //得到player到目标点的导航规划路径
                NavMeshPath path = agent.path;

                if (notDraw)
                {
                    pathStart = path;
                    for (int i = 0; i < path.corners.Length - 1; i++)
                        Debug.DrawLine(path.corners[i], path.corners[i + 1], Color.red);
                    notDraw = false;
                }

                string str_c_position = c_position.ToString();
                string str_steeringTarget = agent.steeringTarget.ToString();
                string str_y = transform.eulerAngles.y.ToString();
                string str_distance = distance.ToString();
                string str_corners_length = path.corners.Length.ToString();
                string direction = retrieveDirection(); //计算旋转方向和角度


                if (sendN)
                {
                    StartCoroutine(SendOnce(str_c_position, str_steeringTarget, str_y, str_distance, str_corners_length, direction));
                }


                if (agent.hasPath && printN)
                {
                    Debug.Log("有路吗:" + agent.hasPath + "，还剩多远:" + distance + "路径拐弯数 is :" + path.corners.Length);
                    Debug.Log("steeringTarget is :" + agent.steeringTarget); //这个就是 path.corners[1]，也就是下一个想去的点的世界坐标
                    Debug.Log("自身的 ratation y is :" + transform.eulerAngles.y + "自身的位置 is :" + c_position);
                    if (path.corners.Length > 2)
                    {
                        Debug.Log("路径的下一些点 is :" + path.corners[0] + path.corners[1] + path.corners[2]);
                    }

                    Debug.Log("===================== sending steeringTarget to server ========================");
                }



            }
            //agent.ResetPath(); // 清除路径，这会让agent停下不动
        }
    }
}