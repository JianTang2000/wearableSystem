using System;
using System.Collections;
using System.Collections.Generic;
using Unity.Collections;
using UnityEngine;


public class LeavePath : MonoBehaviour
{
    private LineRenderer lineRenderer;
    public Queue<Vector3> points;
    public int maxPointCount = 100000;
    private uint count = 0;
    private Transform _transform;
    public bool plot_trajectory = false; //�Ƿ��͵�����Ϣ��������

    public uint sampleFrequence { get; private set; } = 5;

    private void Awake()
    {
        _transform = GetComponent<Transform>();
        lineRenderer = GetComponent<LineRenderer>();
        lineRenderer.positionCount = 0;
        points = new Queue<Vector3>(maxPointCount);
    }

    void Update()
    {
        if (plot_trajectory)
        {
            count += 1;
            if (count % sampleFrequence == 0)
            {
                Vector3 pos = _transform.position;
                //print("============......." + pos.y);
                pos.y = pos.y + 0.1f;  // �ù켣���ڿ� ��һ�㣬��Ȼ���ŵ���������Ⱦbug
                points.Enqueue(pos);
                // if (points.Count > maxPointCount)
                //  {
                //      points.Dequeue();
                //  }
                lineRenderer.positionCount = points.Count;
                lineRenderer.SetPositions(points.ToArray());
            }
        }

    }
}
