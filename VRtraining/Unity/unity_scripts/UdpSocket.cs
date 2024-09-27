

using UnityEngine;
using System.Collections;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

public class UdpSocket : MonoBehaviour
{
    [HideInInspector] public bool isTxStarted = false;


    [SerializeField] string IP = "127.0.0.1"; // local host
    [SerializeField] int rxPort = 8000; // port to receive data from Python on
    [SerializeField] int txPort = 8001; // port to send data to Python on



    // Create necessary UdpClient objects
    UdpClient client;
    IPEndPoint remoteEndPoint;
    Thread receiveThread; // Receiving Thread

    // usage
    private SimpleCharacterController characterController;
    private float[] transformXYZ = new float[3];
    bool yaw_spin_using = false;
    bool training_using = false;
    bool motion_type_time_using = false;
    float motion_type_time = 0f;
    int motion_type_time_count = 0;
    private float[] training_transformXYZ = new float[3];

    bool animation_using = true;
    



    public void SendData(string message) // Use to send data to Python
    {
        try
        {
            byte[] data = Encoding.UTF8.GetBytes(message);
            client.Send(data, data.Length, remoteEndPoint);
        }
        catch (Exception err)
        {
            print(err.ToString());
        }
    }

    public static string GetTimeStamp()
    {
        TimeSpan ts = DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, 0);
        return Convert.ToInt64(ts.TotalMilliseconds).ToString();
    }

    void Awake()
    {
        // Create remote endpoint (to Matlab) 
        remoteEndPoint = new IPEndPoint(IPAddress.Parse(IP), txPort);

        // Create local client
        client = new UdpClient(rxPort);

        // local endpoint define (where messages are received)
        // Create a new thread for reception of incoming messages
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();

        // Initialize (seen in comments window)
        print("UDP Comms Initialised");

        // init input control
        characterController = GetComponent<SimpleCharacterController>();

        characterController.ForwardInput = 0f;


    }

    void FixedUpdate()
    {

        if (motion_type_time_using)
        {
            if (motion_type_time_count > 0)
            {
                motion_type_time_count = motion_type_time_count - 1;
                //print("current motion_type_time_count is ========== " + motion_type_time_count);
                //print("current characterController.ForwardInput is ========== " + characterController.ForwardInput);
            }
            else
            {
                characterController.ForwardInput = 0f;
                characterController.TurnInput = 0f;
                characterController.JumpInput = false;
            }

        }

        if (yaw_spin_using)
        {
            string strNowTime = GetTimeStamp();
            float yaw_float = transformXYZ[1];
            float x = transform.eulerAngles.x;
            float z = transform.eulerAngles.z;
            //print("current yaw from IMU is ......." + strNowTime +"<=====>" + yaw_float);
            transform.eulerAngles = new Vector3(x, yaw_float, z);
            yaw_spin_using = false;
        }

        if (training_using)
        {
            Vector3 update_position = transform.position;
            string strNowTime = GetTimeStamp();
            /*float yaw_float = training_transformXYZ[1];
            float x = transform.eulerAngles.x;
            float z = transform.eulerAngles.z;
            print("current yaw from IMU is ......." + strNowTime + "<=====>" + yaw_float);
            transform.eulerAngles = new Vector3(x, yaw_float, z);*/

            update_position.x = training_transformXYZ[0];
            update_position.y = transform.position.y;
            update_position.z = training_transformXYZ[2];
            transform.position = update_position;
            training_using = false;
        }


    }

    // Receive data, update packets received
    private void ReceiveData()
    {
        while (true)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = client.Receive(ref anyIP);
                string text = Encoding.UTF8.GetString(data);
                print("======> " + text);
                ProcessInput(text);
            }
            catch (Exception err)
            {
                print(err.ToString());
            }
        }
    }

    private void ProcessInput(string input)
    {
        // PROCESS INPUT RECEIVED STRING HERE

        // training
        if (input.Trim().StartsWith("training"))
        {
            string[] subs = input.Split('=');
            float x_coord = (float)Convert.ToDouble(subs[1]);
            float z_coord = (float)Convert.ToDouble(subs[2]);
            //float imu_yaw = (float)Convert.ToDouble(subs[3]);
            training_transformXYZ[0] = x_coord;
            //training_transformXYZ[1] = imu_yaw;
            training_transformXYZ[2] = z_coord;
            training_using = true;
        }
        if (input.Trim().StartsWith("animation"))
        {
            string[] subs = input.Split('=');
            string animation_type = (string)Convert.ToString(subs[1]);
            switch(animation_type)
            {
                case "walk":
                    characterController.ForwardInput = 110f;
                    break;
                case "stop":
                    characterController.ForwardInput = 0f;
                    characterController.TurnInput = 0f;
                    characterController.JumpInput = false; ;
                    break;
            }
        }


            if (input.Trim().StartsWith("yaw_"))
        {
            string[] subs = input.Split('_');
            float yaw_float = (float)Convert.ToDouble(subs[1]);
            transformXYZ[1] = yaw_float;
            yaw_spin_using = true;
            //float x = transform.eulerAngles.x;
            //float z = transform.eulerAngles.z;
            //transform.eulerAngles = new Vector3(x, yaw_float, z);

        }

        if (input.Trim().StartsWith("motion_"))
        {
            
            string[] subs = input.Split('_');
            float motion_time = (float)Convert.ToDouble(subs[2]);
            motion_time = 0.7f;
            string motion_type = (string)Convert.ToString(subs[1]);
            print("receive motion_type_time_count is ========== " + motion_type);
            float vertical_ = 0f;
            float horizontal_ = 0f;
            bool jump_ = false;
            switch (motion_type)
            {
                case "forwardL":
                    vertical_ = 8f;
                    horizontal_ = 0f;
                    print("case left forward");
                    characterController.IsLeft = true;
                    break;
                case "forwardR":
                    vertical_ = 8f;
                    horizontal_ = 0f;
                    print("case right forward");
                    characterController.IsLeft = false;
                    break;
                case "backward":
                    vertical_ = 8f;
                    horizontal_ = 0f;
                    break;
                case "stop":
                    vertical_ = 0f;
                    horizontal_ = 0f;
                    print("case stop");
                    break;
            }
            characterController.ForwardInput = vertical_;  //simpleCharacterController
            characterController.TurnInput = horizontal_;
            characterController.JumpInput = jump_;
            motion_type_time = motion_time;
            motion_type_time_using = true;
            motion_type_time_count = (int)Convert.ToInt16(motion_time / 0.02f)-1;

        }

        if (input.Trim().StartsWith("saved_"))
        {
            float vertical_ = 0f;
            float horizontal_ = 0f;
            bool jump_ = false;

            //print("=========>" + input);

            switch (input)
            {
                case "forward":
                    vertical_ = 1f;
                    horizontal_ = 0f;
                    break;
                case "backward":
                    vertical_ = -1f;
                    horizontal_ = 0f;
                    break;
                case "left":
                    vertical_ = 0f;
                    horizontal_ = -0.1f;
                    break;
                case "right":
                    vertical_ = 0f;
                    horizontal_ = 0.1f;
                    break;
                case "left_m":
                    vertical_ = 0f;
                    horizontal_ = -1f;
                    break;
                case "right_m":
                    vertical_ = 0f;
                    horizontal_ = 1f;
                    break;
                case "stop":
                    vertical_ = 0f;
                    horizontal_ = 0f;
                    break;
            }

            characterController.ForwardInput = vertical_;
            characterController.TurnInput = horizontal_;
            characterController.JumpInput = jump_;
            // fixed update
            //characterController.upd_Update();
        }

        if (!isTxStarted) // First data arrived so tx started
        {
            isTxStarted = true;
        }
    }

    //Prevent crashes - close clients and threads properly!
    void OnDisable()
    {
        if (receiveThread != null)
            receiveThread.Abort();

        client.Close();
    }

}