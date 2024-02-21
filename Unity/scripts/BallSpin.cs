using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using System;
using Random = System.Random;

public class BallSpin : MonoBehaviour
{
    public int target_angle = 34; 
    private float dist = 1f; 
    private Vector3 startPositionCoin;

    // Start is called before the first frame update
    void Start()
    {
        startPositionCoin = transform.position;
        transform.position = startPositionCoin + Quaternion.Euler(Vector3.up * target_angle) * Vector3.forward * dist;
        Debug.Log("************ BallSpin.cs, turn-in-space exp log : ball init at random angle:" + target_angle);
    }

    void Update()
    {
        //transform.Rotate(Vector3.up, 60f * Time.deltaTime, Space.World);
    }
}
