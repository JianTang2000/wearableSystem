using System.Collections;
using UnityEngine.Networking;
using UnityEngine;
using System.Collections.Generic;
using UnityEngine.UI;
using UnityEngine.AI;
using UnityEditor;
using System;






public class playerNavigation : MonoBehaviour
{
    public GameObject target; //ѡһ��Ŀ�꣬��Ҫ��walkable����
    private NavMeshAgent agent; //���󶨵�object��� nav agnet���

    public bool useThis = false; //�Ƿ����ñ��ű�����
    public bool sendN = false; //�Ƿ��͵�����Ϣ��������
    public bool printN = true; //�Ƿ��ӡ��־
    private bool notDraw = true; //һ��ȫ�ֱ������Կ����ڳ�ʼλ�û����켣��
    private NavMeshPath pathStart;
    private NavMeshPath pathCurrent_0419;
    private uint count = 0;
    public uint sampleFrequence { get; private set; } = 60; //�������֡����һ�ε�����Ϣ���Դ��ĵ����ǳ��죬���Բ���Ҫÿ֡����
    private string postUrl = "http://127.0.0.1:8211/userInterface"; //���͵�����Ϣ���������������
    private const string player_position = "player_position";
    private const string steering_target = "steering_target";
    private const string player_rotation_y = "player_rotation_y";
    private const string remaining_distance = "remaining_distance";
    private const string corners_length = "corners_length";
    private const string direciton_name = "direction";

    private void Awake()//��һ�ε��ã���ʼ���ļ�
    {
        agent = GetComponent<NavMeshAgent>();//�������
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
        if (printN) // ѡ���Ƿ��ӡ��־
        {
            if (request.isHttpError || request.isNetworkError)
            {
                Debug.LogError("*************�����������������*************");
                //Debug.LogError(request.error);
            }
            else
            {
                Debug.Log("��������� OK ");
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
        if (angle < 0 || angle >= 360) throw new Exception();
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


    private void Update()
    {
        if (useThis)
        {
            //���û����Ŀ�꣬�Ӷ�������·�����㡣
            agent.SetDestination(target.transform.position);
            agent.isStopped = true; //���������㷨�Զ�����player�ƶ�

            //ÿ��update֮���߻���ʧ������ÿ��update���ѵ�һ�ε�����켣��   ������ĵ�ǰ�滮�켣��  ��һ��
            if (!notDraw)
            {
                //�����켣��
                //Unity ����������߿� ���Ի��Ƶ�������һ�������ߡ�
                for (int i = 0; i < pathStart.corners.Length - 1; i++)
                {
                    Debug.DrawLine(pathStart.corners[i], pathStart.corners[i + 1], Color.red);
                    /*Debug.Log(i + " xpoint:" + pathStart.corners[i]);
                    Debug.Log((i+1) + " xpoint:" + pathStart.corners[i+1]);*/
                }

                //�����켣��
                for (int i = 0; i < pathCurrent_0419.corners.Length - 1; i++)
                {
                    Debug.DrawLine(pathCurrent_0419.corners[i], pathCurrent_0419.corners[i + 1], Color.yellow);
                    //Debug.Log(i + " xpoint:" + path.corners[i].ToString("f4"));
                }


            }


            //����Ƶ��
            count += 1;
            if (count % sampleFrequence == 0 && agent.hasPath)
            {
                //���㵱ǰλ�õ��յ��ʣ�����
                float distance = GetPathRemainingDistance();
                //�õ�player�ĵ�ǰλ��
                Vector3 c_position = transform.position;
                //�õ�player��Ŀ���ĵ����滮·��
                NavMeshPath path = agent.path;

                //�ڵ�һ�ν�����ʱ�򣬰ѳ�ʼ�滮�Ĺ켣�߱����������һ�����
                if (notDraw)
                {
                    pathStart = path;
                    //�����켣��
                    for (int i = 0; i < path.corners.Length - 1; i++)
                    {
                        Debug.DrawLine(path.corners[i], path.corners[i + 1], Color.red);
                        //Debug.Log(i + " xpoint:" + path.corners[i].ToString("f4"));
                    }
                    

                    notDraw = false;
                }
                //�ڷǵ�һ�εĺ���ÿ�ν�����ʱ�򣬰ѵ�ǰ�滮�Ĺ켣�߱�������
                pathCurrent_0419 = path;




                string str_c_position = c_position.ToString();
                string str_steeringTarget = agent.steeringTarget.ToString();
                string str_y = transform.eulerAngles.y.ToString();
                string str_distance = distance.ToString();
                string str_corners_length = path.corners.Length.ToString();
                string direction = retrieveDirection(); //������ת����ͽǶ�
                //Debug.Log("============================direction is " + direction);


                if (sendN)
                {
                    StartCoroutine(SendOnce(str_c_position, str_steeringTarget, str_y, str_distance, str_corners_length, direction));
                }


                if (agent.hasPath && printN)
                {
                    Debug.Log("��·��:" + agent.hasPath + "����ʣ��Զ:" + distance + "·�������� is :" + path.corners.Length);
                    Debug.Log("steeringTarget is :" + agent.steeringTarget); //������� path.corners[1]��Ҳ������һ����ȥ�ĵ����������
                    Debug.Log("����� ratation y is :" + transform.eulerAngles.y + "�����λ�� is :" + c_position);

                    
                    /*for(int path_index = 0;path_index<path.corners.Length;path_index++)
                   
                        //Debug.Log(path_index + " point:" + path.corners[path_index]);
                    }*/

                    if (path.corners.Length > 2)
                    {
                        Debug.Log("·������һЩ�� is :" + path.corners[0] + path.corners[1] + path.corners[2]);
                    }

                    Debug.Log("===================== sending steeringTarget to server ========================");
                }



            }
            //agent.ResetPath(); // ���·���������agentͣ�²���
        }
    }
}