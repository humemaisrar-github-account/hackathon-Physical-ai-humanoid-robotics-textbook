import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './index.module.css';
import type { JSX } from 'react';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/">
            Start Reading 
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />

      <main>
        {/* You can add more sections here, e.g., features, testimonials */}
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              <div className={clsx('col col--6')}>
                <h2>Embodied Intelligence Guide</h2>
                <p>
                  Dive deep into Physical AI and Humanoid Robotics. This textbook provides a comprehensive guide
                  to understanding, building, and deploying intelligent robotic systems.
                </p>
                <p>
                  Explore topics like ROS 2, Digital Twins (Gazebo & Unity), NVIDIA Isaac for AI-Robot Brains,
                  and cutting-edge Vision-Language-Action (VLA) systems.
                </p>
              </div>
              <div className={clsx('col col--6')}>
                <h2>Key Highlights</h2>
                <ul>
                  <li>Modular chapters with learning objectives and practical labs.</li>
                  <li>Hands-on code examples and simulation tutorials.</li>
                  <li>Ethical AI development and Human-Robot Interaction design principles.</li>
                  <li>A final capstone project to integrate all learned concepts.</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}