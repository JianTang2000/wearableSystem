using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class cycleStartArea : MonoBehaviour
{
    public LineRenderer lineRenderer;
    [Range(6, 600)]   
    public int lineCount;       //more lines = smoother ring
    public float radius;
    public float width;

    void Start()
    {
        lineRenderer = GetComponent<LineRenderer>();
        lineRenderer.loop = true;
        Draw();
    }

    void Draw() //Only need to draw when something changes
    {
        lineRenderer.positionCount = lineCount;
        lineRenderer.startWidth = width;
        float theta = (2f * Mathf.PI) / lineCount;  //find radians per segment
        float angle = 0;
        for (int i = 0; i < lineCount; i++)
        {
            float x = transform.position.x + radius * Mathf.Cos(angle);
            float z = transform.position.z + radius * Mathf.Sin(angle);
            lineRenderer.SetPosition(i, new Vector3(x, 1.5f, z));
            //switch 0 and y for 2D games
            angle += theta;
        }
    }
}
