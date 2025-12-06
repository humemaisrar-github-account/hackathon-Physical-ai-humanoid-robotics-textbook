import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './index.module.css';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import { Book, Compass, Cpu, Layers } from 'lucide-react';
import type { JSX } from 'react';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className={styles.heroBanner_container}>
        <div className={styles.heroContent}>
          <h1 className="hero__title">The Dawn of Physical AI</h1>
          <p className="hero__subtitle">
            An open-source textbook on the convergence of robotics, artificial intelligence, and embodied cognition. 
            Master ROS 2, Digital Twins, and advanced Vision-Language-Action models to bring intelligent machines to life.
          </p>
          <div className={styles.buttons}>
            <Link
              className={clsx('button button--secondary button--lg', styles.hero_button)}
              to="/docs/">
              Begin Your Journey
            </Link>
          </div>
        </div>
        <div className={styles.heroImageContainer}>
          <img src="/img/robo.jpg" alt="Physical AI Logo" className={styles.heroImage} />
        </div>
      </div>
    </header>
  );
}

function LearningPath() {
  return (
    <section className={styles.learningPathSection}>
      <div className="container">
        <h2 className={styles.sectionTitle}>Your Learning Path</h2>
        <div className="row">
          <div className={clsx('col col--3', styles.moduleCard)}>
            <div className={styles.moduleCardHeader}>
              <Compass size={32} />
              <h3>Module 1: ROS</h3>
            </div>
            <p>Master the Robot Operating System (ROS 2) to build modular and scalable robot behaviors.</p>
          </div>
          <div className={clsx('col col--3', styles.moduleCard)}>
            <div className={styles.moduleCardHeader}>
              <Layers size={32} />
              <h3>Module 2: Digital Twin</h3>
            </div>
            <p>Create and test in high-fidelity simulations using Gazebo and other modern tools.</p>
          </div>
          <div className={clsx('col col--3', styles.moduleCard)}>
            <div className={styles.moduleCardHeader}>
              <Cpu size={32} />
              <h3>Module 3: Isaac Sim</h3>
            </div>
            <p>Leverage NVIDIA Isaac Sim for realistic, physics-based AI training and validation.</p>
          </div>
          <div className={clsx('col col--3', styles.moduleCard)}>
            <div className={styles.moduleCardHeader}>
              <Book size={32} />
              <h3>Module 4: VLA</h3>
            </div>
            <p>Integrate cutting-edge Vision-Language-Action models for intelligent task execution.</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function CapstoneProject() {
  return (
    <section className={styles.capstoneSection}>
      <div className="container text--center">
        <h2 className={styles.sectionTitle}>Final Capstone Project</h2>
        <p className={styles.capstoneSubtitle}>
          Integrate your skills to build a complete project: an autonomous humanoid robot in a simulated environment
          that can understand and execute natural language commands.
        </p>
        <Link className={clsx('button button--primary button--lg', styles.capstoneButton)} to="/">
          Explore the Capstone
        </Link>
      </div>
    </section>
  );
}

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Physical AI & Humanoid Robotics`}
      description="An open-source textbook on the convergence of robotics, artificial intelligence, and embodied cognition.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        <LearningPath />
        <CapstoneProject />
      </main>
    </Layout>
  );
}