using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ZhuAnimation : MonoBehaviour
{
    Animator ani;
    // Start is called before the first frame update
    void Start()
    {
        ani =  this.transform.GetChild(0).GetComponent<Animator>();
        print("ZHU-Ani");
    }

    // Update is called once per frame
    void Update()
    {
/*        if (Input.GetKey(KeyCode.D))
        {
            ani.SetInteger("play", 1);//right
            //print("ZHU-right");
        }
        else if (Input.GetKey(KeyCode.A))
        {
            ani.SetInteger("play", 2);//left
            //print("ZHU-left");
        }
        else if (Input.GetKey(KeyCode.S))
        {
            ani.SetInteger("play", 0);//stop
            //print("ZHU-stop");
        }
        else
        {
            ani.SetInteger("play", 0);//stop
            //print("ZHU-stop");
        }*/
    }
}
