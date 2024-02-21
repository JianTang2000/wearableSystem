using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class SimpleInput : MonoBehaviour
{

    private SimpleCharacterController characterController;//characterController - 对附加到角色的 SimpleCharacterController 脚本的引用

    private void Awake()
    {
        characterController = GetComponent<SimpleCharacterController>();


    }

    private void FixedUpdate()
    {

        // Read input values and round them. GetAxisRaw works better in this case
        // because of the DecisionRequester, which only gets new decisions periodically.
        int vertical = Mathf.RoundToInt(Input.GetAxisRaw("Vertical"));
        int horizontal = Mathf.RoundToInt(Input.GetAxisRaw("Horizontal"));
        bool jump = Input.GetKey(KeyCode.Space);

        // Convert the actions to Discrete choices (0, 1, 2)
        int v = vertical >= 0 ? vertical : 2;
        int h = horizontal >= 0 ? horizontal : 2;
        int j = jump ? 1 : 0;

        float vertical_ = v <= 1 ? v : -1;
        float horizontal_ = h <= 1 ? h : -1;
        bool jump_ = j > 0;

        characterController.ForwardInput = vertical_;
        characterController.TurnInput = horizontal_;
        characterController.JumpInput = jump_;

    }
}
