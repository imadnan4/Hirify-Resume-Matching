import React, { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Label,
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

const compactTickLabel = (value: any, _index: number): string => {
  if (value === null || value === undefined) {
    return "";
  }

  const text = typeof value === "string" ? value : String(value);
  return text.length > 10 ? `${text.slice(0, 10)}…` : text;
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

function useAnimatedChartData(data: any[]) {
  const [animatedData, setAnimatedData] = useState<any[]>([]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 220);

    return () => clearTimeout(timer);
  }, [data]);

  const xAxisKey = useMemo(() => getXAxisKey(animatedData), [animatedData]);
  const seriesKeys = useMemo(() => getSeriesKeys(animatedData), [animatedData]);

  return { animatedData, xAxisKey, seriesKeys };
}

const AnimatedPieTooltip: React.FC<any> = ({ active, payload }) => {
  if (!active || !payload || !payload.length) {
    return null;
  }

  const point = payload[0]?.payload;
  if (!point) {
    return null;
  }

  const percentageText = typeof point.percentage === "number" ? `${point.percentage.toFixed(1)}%` : "0.0%";
  const valueText = typeof point.value === "number" ? point.value.toFixed(1) : String(point.value ?? 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 6, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className="rounded-lg border border-border/80 bg-card/95 p-3 shadow-xl backdrop-blur"
    >
      <div className="flex items-center gap-2 text-xs font-semibold text-foreground">
        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: point.color || payload[0]?.color }} />
        <span>{point.name}</span>
      </div>
      <div className="mt-1 flex items-center justify-between gap-3 text-xs text-muted-foreground">
        <span>Contribution</span>
        <span className="font-medium text-foreground">{valueText}</span>
      </div>
      <div className="mt-1 flex items-center justify-between gap-3 text-xs text-muted-foreground">
        <span>Share</span>
        <span className="font-medium text-foreground">{percentageText}</span>
      </div>
    </motion.div>
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
  const { animatedData, xAxisKey, seriesKeys } = useAnimatedChartData(data);

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
  const [activeSlice, setActiveSlice] = useState<number | null>(null);
  const gradientPrefix = React.useId().replace(/:/g, "");

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedData(data);
    }, 220);

    return () => clearTimeout(timer);
  }, [data]);

  const chartData = useMemo(() => {
    const source = (animatedData || []).filter((item) => typeof item?.value === "number" && item.value > 0);
    const total = source.reduce((sum: number, item: any) => sum + item.value, 0);

    return source.map((item: any, index: number) => {
      const color = item.color || colors[index % colors.length];
      return {
        ...item,
        color,
        percentage: total > 0 ? (item.value / total) * 100 : 0,
      };
    });
  }, [animatedData, colors]);

  const totalValue = useMemo(
    () => chartData.reduce((sum: number, item: any) => sum + item.value, 0),
    [chartData]
  );

  const centerLabel = title?.toLowerCase().includes("distribution") ? "Distribution" : "Total";

  const labelRenderer = (props: any) => {
    const { cx, cy, midAngle, outerRadius, percent } = props;

    if (typeof percent !== "number" || percent < 0.08) {
      return null;
    }

    const radius = Number(outerRadius || 0) + 14;
    const x = Number(cx || 0) + radius * Math.cos((-midAngle * Math.PI) / 180);
    const y = Number(cy || 0) + radius * Math.sin((-midAngle * Math.PI) / 180);

    return (
      <text
        x={x}
        y={y}
        fill="hsl(var(--muted-foreground))"
        textAnchor={x > Number(cx || 0) ? "start" : "end"}
        dominantBaseline="central"
        fontSize={11}
        fontWeight={600}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

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
          className="relative"
        >
          <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_50%_30%,hsl(var(--primary)/0.08),transparent_58%)]" />
          <ResponsiveContainer width="100%" height={height}>
            <PieChart margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
              <defs>
                {chartData.map((entry: any, index: number) => (
                  <linearGradient
                    key={`${gradientPrefix}-slice-${index}`}
                    id={`${gradientPrefix}-slice-${index}`}
                    x1="0"
                    y1="0"
                    x2="1"
                    y2="1"
                  >
                    <stop offset="0%" stopColor={entry.color} stopOpacity={0.95} />
                    <stop offset="100%" stopColor={entry.color} stopOpacity={0.7} />
                  </linearGradient>
                ))}
              </defs>
              <Pie
                data={[{ name: "track", value: Math.max(totalValue, 1) }]}
                cx="50%"
                cy="46%"
                innerRadius={Math.max(42, Math.floor(height * 0.19))}
                outerRadius={Math.max(68, Math.floor(height * 0.31))}
                dataKey="value"
                stroke="none"
                fill="hsl(var(--muted)/0.55)"
                isAnimationActive={false}
              />
              <Pie
                data={chartData}
                cx="50%"
                cy="46%"
                innerRadius={Math.max(42, Math.floor(height * 0.19))}
                outerRadius={Math.max(68, Math.floor(height * 0.31))}
                dataKey="value"
                nameKey="name"
                startAngle={90}
                endAngle={-270}
                paddingAngle={3}
                cornerRadius={8}
                stroke="hsl(var(--background))"
                strokeWidth={2}
                animationDuration={1200}
                label={labelRenderer}
                labelLine={false}
                onMouseEnter={(_, index) => setActiveSlice(index)}
                onMouseLeave={() => setActiveSlice(null)}
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`${entry.name}-${index}`}
                    fill={`url(#${gradientPrefix}-slice-${index})`}
                    strokeWidth={activeSlice === index ? 3 : 2}
                    opacity={activeSlice === null || activeSlice === index ? 1 : 0.7}
                  />
                ))}
                <Label
                  position="center"
                  content={({ viewBox }) => {
                    if (!viewBox || !("cx" in viewBox) || !("cy" in viewBox)) {
                      return null;
                    }
                    const cx = Number(viewBox.cx);
                    const cy = Number(viewBox.cy);

                    return (
                      <text x={cx} y={cy} textAnchor="middle" dominantBaseline="middle">
                        <tspan x={cx} y={cy - 6} className="fill-foreground text-[16px] font-semibold">
                          {Math.round(totalValue)}
                        </tspan>
                        <tspan x={cx} y={cy + 13} className="fill-muted-foreground text-[10px] font-medium uppercase tracking-[0.08em]">
                          {centerLabel}
                        </tspan>
                      </text>
                    );
                  }}
                />
              </Pie>
              <Tooltip content={<AnimatedPieTooltip />} />
            </PieChart>
          </ResponsiveContainer>

          {chartData.length > 0 ? (
            <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
              {chartData.map((entry: any, index: number) => (
                <motion.div
                  key={`${entry.name}-${index}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25, delay: index * 0.05 }}
                  className="rounded-md border border-border/70 bg-background/80 px-3 py-2"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex min-w-0 items-center gap-2">
                      <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ backgroundColor: entry.color }} />
                      <span className="truncate text-xs font-medium text-foreground">{entry.name}</span>
                    </div>
                    <span className="text-xs font-semibold text-foreground">{entry.value.toFixed(1)}</span>
                  </div>
                  <div className="mt-1 text-[11px] text-muted-foreground">{entry.percentage.toFixed(1)}% of total</div>
                </motion.div>
              ))}
            </div>
          ) : null}
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
  const { animatedData, xAxisKey, seriesKeys } = useAnimatedChartData(data);

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
  const { animatedData, xAxisKey, seriesKeys } = useAnimatedChartData(data);

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
