using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using System;
using Random = System.Random;


public class CoinSpinyawrecoder : MonoBehaviour
{

    private float angle;
    private int angle_2;
    private float dist = 1.5f;
    private Vector3 startPositionCoin;
    // Start is called before the first frame update
    void Start()
    {
        startPositionCoin = transform.position;
        int[] a = new int[] {-34, -30, -20, -10, 0, 10, 20, 30, 34};
        Random ran = new Random();
        int c = ran.Next(a.Length);  // 随机给出数组的一个index
        angle_2 = a[c];
        //int a = Random.Range(0, 4);       
        //float a = Random.Range(0f, 4f);  
        /*        if (angle >= 180f)
                {
                    angle_2 = 50f;
                }
                else
                {
                    angle_2 = 310f;
                }*/
        transform.position = startPositionCoin + Quaternion.Euler(Vector3.up * angle_2) * Vector3.forward * dist;
        Debug.Log("************ CoinSpin.cs, turn-in-space exp log : Coin init at random angle:" + angle_2);
    }

    // Update is called once per frame
    void Update()
    {
        // disable 旋转
        //transform.Rotate(Vector3.up, 60f * Time.deltaTime, Space.World);
    }
}
