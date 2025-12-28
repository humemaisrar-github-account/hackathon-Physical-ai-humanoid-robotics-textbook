import React from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: React.ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Master the Robotics Core',
    description: (
      <>
        Build a rock-solid foundation in modern robotics. Dive deep into the Robot Operating System (ROS 2), exploring its powerful architecture for creating modular and scalable robot behaviors.
      </>
    ),
  },
  {
    title: 'Build & Test in the Metaverse',
    description: (
      <>
        Create and validate complex robotic systems in high-fidelity simulations. Learn to build Digital Twins using Gazebo and leverage the power of NVIDIA Isaac Sim for realistic, physics-based testing.
      </>
    ),
  },
  {
    title: 'Deploy Intelligent Brains',
    description: (
      <>
        Go beyond simple automation. Integrate cutting-edge AI into your robots, exploring Vision-Language-Action (VLA) models that allow for natural language interaction and complex task execution.
      </>
    ),
  },
];

function Feature({title, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className={styles.featureCard}>
        <Heading as="h3" className={styles.featureCard_title}>{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): React.ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
