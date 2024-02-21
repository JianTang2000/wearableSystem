// Patrol.cs
using UnityEngine;
using UnityEngine.AI;
using System.Collections;



public class Patrol : MonoBehaviour
{

    public Transform[] points;
    public bool doNav = false;
    private int destPoint = 0;
    private NavMeshAgent agent;


    void Start()
    {
        agent = GetComponent<NavMeshAgent>();


        agent.autoBraking = false;

        if (doNav)
        {
            GotoNextPoint();
        }
    }


    void GotoNextPoint()
    {

        if (points.Length == 0)
            return;


        agent.destination = points[destPoint].position;


        destPoint = (destPoint + 1) % points.Length;
    }


    void Update()
    {
        if (doNav)
        {

            if (!agent.pathPending && agent.remainingDistance < 0.5f)
                GotoNextPoint();
        }

    }
}