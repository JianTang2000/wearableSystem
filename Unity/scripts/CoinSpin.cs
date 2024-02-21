using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using System;
using Random = System.Random;


public class CoinSpin : MonoBehaviour
{

    public int target_angle = 34; //每次重启前需要随机指定
    private float dist = 1.5f; // 硬币向前移动的距离
    private Vector3 startPositionCoin;

    // Start is called before the first frame update
    void Start()
    {
        //coin一开始时在中心位置，然后随机给一个角度，并移动到1.5远处位置
        startPositionCoin = transform.position;
        transform.position = startPositionCoin + Quaternion.Euler(Vector3.up * target_angle) * Vector3.forward * dist;
        Debug.Log("************ CoinSpin.cs, turn-in-space exp log : Coin init at random angle:" + target_angle);
    }

    // Update is called once per frame
    void Update()
    {
        // 旋转
        //transform.Rotate(Vector3.up, 60f * Time.deltaTime, Space.World);
    }
}
