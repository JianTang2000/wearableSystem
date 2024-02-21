using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class z_test : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        float x = transform.eulerAngles.x;
        float z = transform.eulerAngles.z;
        transform.eulerAngles = new Vector3(x, 90, z);

    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
