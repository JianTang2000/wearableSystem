using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SimpleCharacterController : MonoBehaviour
{
    [Tooltip("Maximum slope the character can jump on")]
    [Range(5f, 60f)]
    public float slopeLimit = 45f;
    [Tooltip("Move speed in meters/second")]
    public float moveSpeed = 5f;  
    [Tooltip("Turn speed in degrees/second, left (+) or right (-)")]
    public float turnSpeed = 300;
    [Tooltip("Whether the character can jump")]
    public bool allowJump = false;
    [Tooltip("Upward speed to apply when jumping in meters/second")]
    public float jumpSpeed = 4f;

    // debug usage 
    private float forward_count = 0f;



    public bool IsGrounded { get; private set; }
    public float ForwardInput { get; set; }

    public bool IsLeft { get; set; }  

    public float TurnInput { get; set; }
    public bool JumpInput { get; set; }

    new private Rigidbody rigidbody;
    private CapsuleCollider capsuleCollider;
    private Animator animator;

    private bool udp_animator = true; 

    void Start()
    {
        //animator = this.transform.GetChild(0).GetComponent<Animator>();
        animator = this.transform.GetComponentInChildren<Animator>();
    }

    void moveAnimation()
    {
        if (Input.GetKey(KeyCode.W))
        {
            //Debug.Log("Forward:");
            animator.SetBool("forward", true);
        }
        else
        {
            animator.SetBool("forward", false);
        }
        if (Input.GetKey(KeyCode.S))
        {
            animator.SetBool("backward", true);
        }
        else
        {
            animator.SetBool("backward", false);
        }
    }

    private void Awake()
    {
        rigidbody = GetComponent<Rigidbody>();
        capsuleCollider = GetComponent<CapsuleCollider>();
    }




    private void FixedUpdate()
    {

        CheckGrounded();
        ProcessActions();
        /*if(IsGrounded && udp_animator && (ForwardInput > 0f))
        {
            print("fixed update-animator");
        }*/


        //moveAnimation();  // UDP
    }



    public void CheckGrounded()
    {
        IsGrounded = false;
        float capsuleHeight = Mathf.Max(capsuleCollider.radius * 2f, capsuleCollider.height);
        Vector3 capsuleBottom = transform.TransformPoint(capsuleCollider.center - Vector3.up * capsuleHeight / 2f);
        float radius = transform.TransformVector(capsuleCollider.radius, 0f, 0f).magnitude;
        Ray ray = new Ray(capsuleBottom + transform.up * .01f, -transform.up);
        RaycastHit hit;
        if (Physics.Raycast(ray, out hit, radius * 5f))
        {
            float normalAngle = Vector3.Angle(hit.normal, transform.up);
            if (normalAngle < slopeLimit)
            {
                float maxDist = radius / Mathf.Cos(Mathf.Deg2Rad * normalAngle) - radius + .02f;
                if (hit.distance < maxDist)
                    IsGrounded = true;
            }
        }
        //print("is grounded ? =================" + IsGrounded);
        IsGrounded = true;
    }

    public void ProcessActions()
    {
        // Process Turning
        if (TurnInput != 0f)
        {
            float angle = Mathf.Clamp(TurnInput, -1f, 1f) * turnSpeed;
            transform.Rotate(Vector3.up, Time.fixedDeltaTime * angle);
        }
        // Process Movement/Jumping
        if (IsGrounded)
        {
            // Reset the velocity
            rigidbody.velocity = Vector3.zero;
            // Check if trying to jump
            if (JumpInput && allowJump)//�������������ж�
            {
                // Apply an upward velocity to jump
                rigidbody.velocity += Vector3.up * jumpSpeed;
            }

            // Apply a forward or backward velocity based on player input
            /*            if (ForwardInput > 0.1f | ForwardInput < -0.1f)
                        {
                            forward_count = forward_count + 1f;
                            print("forward count is ===>" + forward_count + ", speed is " + ForwardInput + "*" + moveSpeed);
                        }*/


            if (udp_animator)
            {
                if (ForwardInput > 0f)
                {
                    
                    animator.SetBool("forward", true);
                    /*if (IsLeft)
                    {
                        //print("animator forward left .......");
                        animator.SetInteger("play", 2);//left
                        //������Ŷ���
                    }
                    else
                    {
                        animator.SetInteger("play", 1);//right
                        //print("animator forward right .......");
                    }*/
                }
                else
                {
                    if (ForwardInput < 0f)
                    {
                        //print("animator back.......");
                        //animator.SetBool("backward", true);
                    }
                    else
                    {
                        animator.SetBool("forward", false);
                        //animator.SetBool("backward", false);
                        animator.SetInteger("play", 0);//stop
                    }
                }


            }

            if (ForwardInput != 110f) {
                rigidbody.velocity += transform.forward * Mathf.Clamp(ForwardInput, -1f, 1f) * moveSpeed;
            }

            



        }
        else
        {
            // Check if player is trying to change forward/backward movement while jumping/falling
            if (!Mathf.Approximately(ForwardInput, 0f))
            {
                // Override just the forward velocity with player input at half speed
                Vector3 verticalVelocity = Vector3.Project(rigidbody.velocity, Vector3.up);
                rigidbody.velocity = verticalVelocity + transform.forward * Mathf.Clamp(ForwardInput, -1f, 1f) * moveSpeed / 2f;
            }
        }
    }


}
