using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.AI;





public class nav2point : MonoBehaviour
{
    public GameObject target;
    public bool doNav = false;
    private NavMeshAgent agent;

    private uint count = 0;
    private bool printN = false;
    public uint sampleFrequence { get; private set; } = 99;

    private void Awake()//第一次调用，初始化文件
    {
        agent = GetComponent<NavMeshAgent>();//调用组件

    }
    private void Update()
    {
        if (doNav)
        {
            //设置或更新目标，从而触发新路径计算。
            agent.SetDestination(target.transform.position);//定位物体二即目标的位置


            count += 1;
            if (count % sampleFrequence == 0 && printN)
            {
                //Debug.Log("remain distance is :" + agent.remainingDistance);
                //Debug.Log("path is :" + agent.path);
                //Debug.Log("steeringTarget is :" + agent.steeringTarget);
                //Debug.Log("================================================================");
            }
            //this.transform.Translate(0, 0, 0);//让它静止
            //agent.ResetPath(); // 清除路径，这会让agent停下不动
        }





    }
}