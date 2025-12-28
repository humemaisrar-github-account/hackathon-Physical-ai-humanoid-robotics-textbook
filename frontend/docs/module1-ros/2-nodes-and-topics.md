---
title: "2. ROS 2 Nodes and Topics"
---

## Learning Objectives

- Understand the concept of ROS 2 nodes.
- Learn how to create and manage ROS 2 topics.
- Exchange messages between nodes using topics.

## ROS 2 Nodes

In ROS 2, a node is an executable process that performs computation. Nodes are typically designed to do one thing well, such as controlling a motor, reading sensor data, or performing a specific algorithm. A ROS 2 system usually consists of many nodes working together.

## ROS 2 Topics

Topics are a fundamental communication mechanism in ROS 2. They implement a publish-subscribe messaging pattern. A node can "publish" messages to a named topic, and any number of other nodes can "subscribe" to that topic to receive those messages. This allows for loose coupling between components, as publishers and subscribers don't need to know about each other directly.

### Message Types

When publishing or subscribing to a topic, you must specify a message type. This type defines the structure of the data that will be sent over the topic. Common message types include `std_msgs/msg/String` for simple text, `geometry_msgs/msg/Twist` for velocity commands, and `sensor_msgs/msg/Image` for camera data.

## Code Example: Simple Publisher and Subscriber

Let's create a "Hello World" example using a Python publisher and subscriber.

### Publisher Node (`minimal_publisher.py`)

This node will publish the string "Hello ROS 2" to a topic named `topic` every half-second.

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello ROS 2: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Subscriber Node (`minimal_subscriber.py`)

This node will subscribe to the `topic` and print the received messages to the console.

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Practical Lab: Running Your First ROS 2 Nodes

1.  **Create a ROS 2 Workspace**: If you don't have one, create a new ROS 2 workspace:
    ```bash
    mkdir -p ~/ros2_ws/src
    cd ~/ros2_ws
    colcon build
    ```
2.  **Create a Python Package**: Inside `~/ros2_ws/src`, create a new Python package for your nodes:
    ```bash
    ros2 pkg create --build-type ament_python my_ros_pkg
    ```
3.  **Place the Code**: Save `minimal_publisher.py` and `minimal_subscriber.py` into `~/ros2_ws/src/my_ros_pkg/my_ros_pkg/`.
4.  **Update `setup.py`**: In `~/ros2_ws/src/my_ros_pkg/setup.py`, add the entry points for your executables.
    ```python
    entry_points={
        'console_scripts': [
            'minimal_publisher = my_ros_pkg.minimal_publisher:main',
            'minimal_subscriber = my_ros_pkg.minimal_subscriber:main',
        ],
    },
    ```
5.  **Build the Workspace**:
    ```bash
    cd ~/ros2_ws
    colcon build
    ```
6.  **Source the Setup Files**: Open two separate terminal windows. In each, source your workspace:
    ```bash
    source install/setup.bash # or setup.zsh
    ```
7.  **Run the Publisher**: In the first terminal:
    ```bash
    ros2 run my_ros_pkg minimal_publisher
    ```
8.  **Run the Subscriber**: In the second terminal:
    ```bash
    ros2 run my_ros_pkg minimal_subscriber
    ```
    You should see the subscriber printing the messages published by the publisher.

## Safety and Ethics Notes

When designing robotic communication systems, consider the security implications of data exchange. Ensure sensitive data is handled securely and that critical commands are authenticated. The reliability of topic communication is crucial for safe robot operation; unexpected message loss can lead to unpredictable behavior.

## Summary

This chapter delved into the core ROS 2 concepts of nodes and topics, demonstrating how they form the backbone of inter-process communication in a robotic system. Through practical examples, we learned to create and run simple publisher and subscriber nodes in Python, laying the groundwork for more complex robotic applications.