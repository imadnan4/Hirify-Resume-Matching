import React, { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "./card";

interface AnimatedChartProps {
  data: any[];
  title?: string;
  className?: string;
  height?: number;
  colors?: string[];
  animationDuration?: number;
}

const EVIL_CHART_PALETTE = [
  "#22D3EE",
  "#38BDF8",
  "#60A5FA",
  "#818CF8",
  "#34D399",
  "#F59E0B",
];

const CHART_CARD_CLASS = "w-full overflow-hidden border border-border/60 bg-card/95 shadow-sm";

const AXIS_TICK_STYLE = {
  fontSize: 12,
  fill: "hsl(var(--muted-foreground))",
};

const compactTickLabel = (value: unknown) => {
  if (typeof value !== "string") {
    return value;
  }

  return value.length > 10 ? `${value.slice(0, 10)}…` : value;
};

const getXAxisKey = (data: any[]) => {
  const sample = data.find(Boolean);

  if (!sample) {
    return "name";
  }

  const candidates = ["name", "date", "month", "label"];
  return candidates.find((key) => key in sample) || Object.keys(sample)[0] || "name";
};

const getSeriesKeys = (data: any[]) => {
  const sample = data.find(Boolean);
  if (!sample) {
    return [];
  }

  return Object.keys(sample).filter(
    (key) => !["name", "date", "month", "label", "color"].includes(key),
  );
};

const AnimatedTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 6, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className="rounded-lg border border-border/80 bg-card/95 p-3 shadow-xl backdrop-blur"
    >
      {label ? <p className="mb-1 text-xs font-semibold text-foreground/90">{label}</p> : null}
      <div className="flex flex-col gap-1">
        {payload.map((entry: any, index: number) => (
          <div key={`${entry.name}-${index}`} className="flex items-center justify-between gap-3 text-xs">
            <span className="font-medium" style={{ color: entry.color }}>
              {entry.name}
            </span>
            <span className="text-muted-foreground">{entry.value}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
};

export const AnimatedBarChart: React.FC<AnimatedChartProps> = ({
  data,
  title,
  className,
  height = 280,
  colors = EVIL_CHART_PALETTE,
  animationDuration = 1100,
}) => {
  const [animatedData, setAnimatedData] = useState<any[]>([]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 220);

    return () => clearTimeout(timer);
  }, [data]);

  const xAxisKey = useMemo(() => getXAxisKey(animatedData), [animatedData]);
  const seriesKeys = useMemo(() => getSeriesKeys(animatedData), [animatedData]);

  return (
    <Card className={cn(CHART_CARD_CLASS, className)}>
      {title ? (
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-semibold tracking-tight">{title}</CardTitle>
        </CardHeader>
      ) : null}
      <CardContent className="pt-4">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
        >
          <ResponsiveContainer width="100%" height={height}>
            <BarChart data={animatedData} margin={{ top: 12, right: 8, left: -14, bottom: 0 }}>
              <CartesianGrid vertical={false} strokeDasharray="4 4" stroke="hsl(var(--border))" strokeOpacity={0.45} />
              <XAxis
                dataKey={xAxisKey}
                tickLine={false}
                axisLine={false}
                tickMargin={10}
                minTickGap={16}
                tick={AXIS_TICK_STYLE}
                tickFormatter={compactTickLabel}
              />
              <YAxis tickLine={false} axisLine={false} width={30} tick={AXIS_TICK_STYLE} />
              <Tooltip cursor={{ fill: "hsl(var(--muted))", opacity: 0.25 }} content={<AnimatedTooltip />} />
              {seriesKeys.length > 1 ? <Legend iconType="circle" wrapperStyle={{ fontSize: "12px" }} /> : null}
              {seriesKeys.map((key, index) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={colors[index % colors.length]}
                  radius={[8, 8, 2, 2]}
                  maxBarSize={34}
                  animationDuration={animationDuration}
                >
                  {seriesKeys.length === 1 ? (
                    <LabelList
                      dataKey={key}
                      position="top"
                      fontSize={11}
                      fill="hsl(var(--muted-foreground))"
                      formatter={(value: unknown) =>
                        typeof value === "number" ? Math.round(value).toString() : String(value)
                      }
                    />
                  ) : null}
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
  height = 280,
  colors = EVIL_CHART_PALETTE,
}) => {
  const [animatedData, setAnimatedData] = useState<any[]>([]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 220);

    return () => clearTimeout(timer);
  }, [data]);

  return (
    <Card className={cn(CHART_CARD_CLASS, className)}>
      {title ? (
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-semibold tracking-tight">{title}</CardTitle>
        </CardHeader>
      ) : null}
      <CardContent className="pt-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.45 }}
        >
          <ResponsiveContainer width="100%" height={height}>
            <PieChart margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <Pie
                data={animatedData}
                cx="50%"
                cy="48%"
                innerRadius={Math.max(32, Math.floor(height * 0.17))}
                outerRadius={Math.max(52, Math.floor(height * 0.28))}
                dataKey="value"
                nameKey="name"
                paddingAngle={2}
                stroke="hsl(var(--background))"
                strokeWidth={2}
                animationDuration={1200}
              >
                {animatedData.map((entry, index) => (
                  <Cell key={`${entry.name}-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip content={<AnimatedTooltip />} />
              <Legend verticalAlign="bottom" iconType="circle" wrapperStyle={{ fontSize: "12px", paddingTop: 8 }} />
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
  height = 280,
  colors = EVIL_CHART_PALETTE,
  animationDuration = 1100,
}) => {
  const [animatedData, setAnimatedData] = useState<any[]>([]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 220);

    return () => clearTimeout(timer);
  }, [data]);

  const xAxisKey = useMemo(() => getXAxisKey(animatedData), [animatedData]);
  const seriesKeys = useMemo(() => getSeriesKeys(animatedData), [animatedData]);

  return (
    <Card className={cn(CHART_CARD_CLASS, className)}>
      {title ? (
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-semibold tracking-tight">{title}</CardTitle>
        </CardHeader>
      ) : null}
      <CardContent className="pt-4">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
        >
          <ResponsiveContainer width="100%" height={height}>
            <LineChart data={animatedData} margin={{ top: 12, right: 8, left: -14, bottom: 0 }}>
              <CartesianGrid vertical={false} strokeDasharray="4 4" stroke="hsl(var(--border))" strokeOpacity={0.45} />
              <XAxis
                dataKey={xAxisKey}
                tickLine={false}
                axisLine={false}
                tickMargin={10}
                minTickGap={16}
                tick={AXIS_TICK_STYLE}
                tickFormatter={compactTickLabel}
              />
              <YAxis tickLine={false} axisLine={false} width={30} tick={AXIS_TICK_STYLE} />
              <Tooltip content={<AnimatedTooltip />} />
              {seriesKeys.length > 1 ? <Legend iconType="circle" wrapperStyle={{ fontSize: "12px" }} /> : null}
              {seriesKeys.map((key, index) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 4 }}
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
  height = 280,
  colors = EVIL_CHART_PALETTE,
  animationDuration = 1100,
}) => {
  const [animatedData, setAnimatedData] = useState<any[]>([]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 220);

    return () => clearTimeout(timer);
  }, [data]);

  const xAxisKey = useMemo(() => getXAxisKey(animatedData), [animatedData]);
  const seriesKeys = useMemo(() => getSeriesKeys(animatedData), [animatedData]);

  return (
    <Card className={cn(CHART_CARD_CLASS, className)}>
      {title ? (
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-semibold tracking-tight">{title}</CardTitle>
        </CardHeader>
      ) : null}
      <CardContent className="pt-4">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
        >
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={animatedData} margin={{ top: 12, right: 8, left: -14, bottom: 0 }}>
              <defs>
                {seriesKeys.map((key, index) => {
                  const color = colors[index % colors.length];
                  const gradientId = `${key}-gradient`;
                  return (
                    <linearGradient key={gradientId} id={gradientId} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={color} stopOpacity={0.42} />
                      <stop offset="95%" stopColor={color} stopOpacity={0.04} />
                    </linearGradient>
                  );
                })}
              </defs>
              <CartesianGrid vertical={false} strokeDasharray="4 4" stroke="hsl(var(--border))" strokeOpacity={0.45} />
              <XAxis
                dataKey={xAxisKey}
                tickLine={false}
                axisLine={false}
                tickMargin={10}
                minTickGap={16}
                tick={AXIS_TICK_STYLE}
                tickFormatter={compactTickLabel}
              />
              <YAxis tickLine={false} axisLine={false} width={30} tick={AXIS_TICK_STYLE} />
              <Tooltip content={<AnimatedTooltip />} />
              {seriesKeys.length > 1 ? <Legend iconType="circle" wrapperStyle={{ fontSize: "12px" }} /> : null}
              {seriesKeys.map((key, index) => {
                const color = colors[index % colors.length];
                return (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={color}
                    fill={`url(#${key}-gradient)`}
                    strokeWidth={2.2}
                    animationDuration={animationDuration}
                    activeDot={{ r: 4 }}
                  />
                );
              })}
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>
      </CardContent>
    </Card>
  );
};

interface ChartGridProps {
  charts: Array<{
    component: React.ReactElement;
    title?: string;
    colSpan?: number;
  }>;
  columns?: number;
  className?: string;
}

export const ChartGrid: React.FC<ChartGridProps> = ({ charts, columns = 2, className }) => {
  const columnsClass =
    columns >= 4 ? "md:grid-cols-4" : columns === 3 ? "md:grid-cols-3" : columns === 1 ? "md:grid-cols-1" : "md:grid-cols-2";

  return (
    <div className={cn("grid grid-cols-1 gap-6", columnsClass, className)}>
      {charts.map((chart, index) => {
        const colSpanClass = chart.colSpan === 2 ? "md:col-span-2" : chart.colSpan === 3 ? "md:col-span-3" : "";

        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.08 }}
            className={colSpanClass}
          >
            {chart.component}
          </motion.div>
        );
      })}
    </div>
  );
};

export default AnimatedBarChart;
