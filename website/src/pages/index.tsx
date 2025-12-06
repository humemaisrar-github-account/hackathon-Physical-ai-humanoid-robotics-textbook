import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './index.module.css';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import type { JSX } from 'react';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className={styles.heroBanner_container}>
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
    </header>
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
      </main>
    </Layout>
  );
}