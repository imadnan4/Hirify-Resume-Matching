import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart,
  LabelList,
} from 'recharts';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from './card';

interface AnimatedChartProps {
  data: any[];
  title?: string;
  className?: string;
  height?: number;
  colors?: string[];
  animationDuration?: number;
}

// Custom animated bar component
const AnimatedBar: React.FC<any> = (props) => {
  const [animatedHeight, setAnimatedHeight] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedHeight(props.height);
    }, props.animationBegin || 0);

    return () => clearTimeout(timer);
  }, [props.height, props.animationBegin]);

  return (
    <motion.rect
      {...props}
      height={animatedHeight}
      animate={{ height: animatedHeight }}
      transition={{ duration: 0.8, delay: props.animationBegin / 1000 }}
    />
  );
};

// Custom tooltip with animations
const AnimatedTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-card border border-border rounded-lg p-3 shadow-lg"
      >
        <p className="font-medium text-sm">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </motion.div>
    );
  }
  return null;
};

export const AnimatedBarChart: React.FC<AnimatedChartProps> = ({
  data,
  title,
  className,
  height = 400,
  colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c'],
  animationDuration = 1500,
}) => {
  const [animatedData, setAnimatedData] = useState<any[]>([]);

  useEffect(() => {
    // Animate data entry
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 300);

    return () => clearTimeout(timer);
  }, [data]);

  return (
    <Card className={cn('w-full', className)}>
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <ResponsiveContainer width="100%" height={height}>
            <BarChart data={animatedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip content={<AnimatedTooltip />} />
              <Legend />
              {animatedData.length > 0 && Object.keys(animatedData[0] || {})
                .filter((key) => key !== 'name')
                .map((key, index) => (
                  <Bar
                    key={key}
                    dataKey={key}
                    fill={colors[index % colors.length]}
                    animationDuration={animationDuration}
                  >
                    <LabelList 
                      dataKey={key} 
                      position="top" 
                      formatter={(value) => {
                        if (typeof value === 'number') {
                          return `${key === 'userScore' ? 'User' : 'Target'}: ${value.toFixed(1)}%`
                        }
                        return `${key}: ${value}`
                      }} 
                      fontSize={10}
                      fill="#666"
                    />
                  </Bar>
                ))}
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </CardContent>
    </Card>
  );
};

export const AnimatedPieChart: React.FC<AnimatedChartProps> = ({
  data,
  title,
  className,
  height = 400,
  colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'],
}) => {
  const [animatedData, setAnimatedData] = useState<any[]>([]);

  useEffect(() => {
    // Animate data entry
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 300);

    return () => clearTimeout(timer);
  }, [data]);

  return (
    <Card className={cn('w-full', className)}>
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent>
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
        >
          <ResponsiveContainer width="100%" height={height}>
            <PieChart>
              <Pie
                data={animatedData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                animationDuration={1500}
              >
                {animatedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip content={<AnimatedTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </CardContent>
    </Card>
  );
};

export const AnimatedLineChart: React.FC<AnimatedChartProps> = ({
  data,
  title,
  className,
  height = 400,
  colors = ['#8884d8', '#82ca9d', '#ffc658'],
  animationDuration = 1500,
}) => {
  const [animatedData, setAnimatedData] = useState<any[]>([]);

  useEffect(() => {
    // Animate data entry
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 300);

    return () => clearTimeout(timer);
  }, [data]);

  return (
    <Card className={cn('w-full', className)}>
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <ResponsiveContainer width="100%" height={height}>
            <LineChart data={animatedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip content={<AnimatedTooltip />} />
              <Legend />
              {Object.keys(data[0] || {})
                .filter((key) => key !== 'name')
                .map((key, index) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={colors[index % colors.length]}
                    strokeWidth={2}
                    animationDuration={animationDuration}
                  />
                ))}
            </LineChart>
          </ResponsiveContainer>
        </motion.div>
      </CardContent>
    </Card>
  );
};

export const AnimatedAreaChart: React.FC<AnimatedChartProps> = ({
  data,
  title,
  className,
  height = 400,
  colors = ['#8884d8', '#82ca9d', '#ffc658'],
  animationDuration = 1500,
}) => {
  const [animatedData, setAnimatedData] = useState<any[]>([]);

  useEffect(() => {
    // Animate data entry
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 300);

    return () => clearTimeout(timer);
  }, [data]);

  return (
    <Card className={cn('w-full', className)}>
      {title && (
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
      )}
      <CardContent>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={animatedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip content={<AnimatedTooltip />} />
              <Legend />
              {Object.keys(data[0] || {})
                .filter((key) => key !== 'name')
                .map((key, index) => (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stackId="1"
                    stroke={colors[index % colors.length]}
                    fill={colors[index % colors.length]}
                    fillOpacity={0.6}
                    animationDuration={animationDuration}
                  />
                ))}
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>
      </CardContent>
    </Card>
  );
};

// Chart grid component for displaying multiple charts
interface ChartGridProps {
  charts: Array<{
    component: React.ReactElement;
    title?: string;
    colSpan?: number;
  }>;
  columns?: number;
  className?: string;
}

export const ChartGrid: React.FC<ChartGridProps> = ({
  charts,
  columns = 2,
  className,
}) => {
  return (
    <div className={cn('grid gap-6', `grid-cols-1 md:grid-cols-${columns}`, className)}>
      {charts.map((chart, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
          className={chart.colSpan ? `col-span-${chart.colSpan}` : ''}
        >
          {chart.component}
        </motion.div>
      ))}
    </div>
  );
};

export default AnimatedBarChart;
