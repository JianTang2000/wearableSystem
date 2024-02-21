using System.Collections;
using System.Collections.Generic;
using UnityEngine;
 
public class BallDrawLine : MonoBehaviour
{
    private LineRenderer lineRenderer;
    public Queue<Vector3> points;
    public int maxPointCount = 2;
    private Transform _transform;
    Vector3[] pos_end = new Vector3[1]; 
    private float dist = 1.4f; 

    void Start()
    {
        _transform = GetComponent<Transform>();
        lineRenderer = GetComponent<LineRenderer>();
        lineRenderer.positionCount = 0;
        points = new Queue<Vector3>(maxPointCount);
    }

    void Update()
    {
        if (points.Count > 0)
          {
              points.Dequeue();
          }
        if (points.Count > 0)
        {
            points.Dequeue();
        }

        Vector3 pos = _transform.position;
        Vector3 pos_bottom = _transform.position;
        pos.y = pos.y + 0.4f;  
        points.Enqueue(pos);

        pos_end[0] = pos_bottom + Quaternion.Euler(Vector3.up * transform.eulerAngles.y) * Vector3.forward * dist;
        points.Enqueue(pos_end[0]);

        lineRenderer.positionCount = points.Count;
        lineRenderer.SetPositions(points.ToArray());
    }


}
