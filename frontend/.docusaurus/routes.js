import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '735'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', 'caf'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '157'),
            routes: [
              {
                path: '/docs/',
                component: ComponentCreator('/docs/', '2d9'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/capstone/capstone-overview',
                component: ComponentCreator('/docs/capstone/capstone-overview', 'e77'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/category/capstone-autonomous-humanoid-project',
                component: ComponentCreator('/docs/category/capstone-autonomous-humanoid-project', 'adc'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/category/module-1-ros-2--robotic-nervous-system',
                component: ComponentCreator('/docs/category/module-1-ros-2--robotic-nervous-system', '52b'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/category/module-2-digital-twin--gazebo--unity',
                component: ComponentCreator('/docs/category/module-2-digital-twin--gazebo--unity', 'd5b'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/category/module-3-nvidia-isaac--ai-robot-brain',
                component: ComponentCreator('/docs/category/module-3-nvidia-isaac--ai-robot-brain', '614'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/category/module-4-vla-systems--vision-language-action',
                component: ComponentCreator('/docs/category/module-4-vla-systems--vision-language-action', 'aa9'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/chatbot',
                component: ComponentCreator('/docs/chatbot', '587'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/glossary',
                component: ComponentCreator('/docs/glossary', 'ff0'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/module1-ros/introduction-to-ros',
                component: ComponentCreator('/docs/module1-ros/introduction-to-ros', 'a76'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/module1-ros/nodes-and-topics',
                component: ComponentCreator('/docs/module1-ros/nodes-and-topics', '44c'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/module2-digital-twin/gazebo-basics',
                component: ComponentCreator('/docs/module2-digital-twin/gazebo-basics', '765'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/module2-digital-twin/understanding-simulation',
                component: ComponentCreator('/docs/module2-digital-twin/understanding-simulation', '7c5'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/module3-isaac/intro-to-isaac-sim',
                component: ComponentCreator('/docs/module3-isaac/intro-to-isaac-sim', '974'),
                exact: true,
                sidebar: "modulesSidebar"
              },
              {
                path: '/docs/module4-vla/vla-introduction',
                component: ComponentCreator('/docs/module4-vla/vla-introduction', '5ba'),
                exact: true,
                sidebar: "modulesSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
