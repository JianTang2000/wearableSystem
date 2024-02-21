using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// 在 可能生成的位置 画一个圈儿，仅仅为了获得更好的展示效果，没有什么实际的用处
//https://stackoverflow.com/questions/13708395/how-can-i-draw-a-circle-in-unity3d   --参考
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
