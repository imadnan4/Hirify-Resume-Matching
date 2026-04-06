import * as React from "react";
import { Button as ButtonPrimitive } from "@base-ui/react/button";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "focus-visible:border-ring focus-visible:ring-ring/30 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive dark:aria-invalid:border-destructive/50 border border-transparent bg-clip-padding text-xs/relaxed font-medium focus-visible:ring-[2px] aria-invalid:ring-[2px] [&_svg:not([class*='size-'])]:size-4 inline-flex items-center justify-center whitespace-nowrap transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none shrink-0 [&_svg]:shrink-0 outline-none group/button select-none gap-2! rounded-lg [&_svg]:pointer-events-none [&_svg]:size-4 cursor-pointer aria-expanded:ring-[2px] aria-expanded:ring-ring/30",
  {
    variants: {
      variant: {
        default:
          "bg-radial-[at_52%_-52%] [text-shadow:0_1px_0_var(--color-primary)] border-primary bg-background from-primary/70 to-primary/95 hover:from-primary/80 hover:to-primary/100 text-primary-foreground inset-shadow-2xs inset-shadow-white/25 border shadow-md shadow-zinc-950/30",
        secondary:
          "shadow-xs bg-linear-to-t hover:to-muted to-sidebar from-muted bg-background dark:from-muted/50 dark:border-border border border-zinc-300 shadow-zinc-950/10 text-foreground",
        decorations:
          "shadow-xs hover:bg-muted bg-background dark:border-border border border-zinc-300 shadow-zinc-950/10 text-foreground",
        muted:
          "bg-muted hover:bg-neutral-200 dark:hover:bg-accent shadow-zinc-950/10 duration-200 text-foreground",
        outline:
          "border-border dark:bg-input/20 dark:bg-input/30 hover:bg-input/50 hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground",
        ghost:
          "hover:bg-neutral-200 dark:hover:bg-accent hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground",
        info:
          "text-white [text-shadow:0_1px_0_theme(colors.blue.900)] bg-gradient-to-b from-blue-600 to-blue-700 shadow-md shadow-zinc-950/20 ring-1 ring-inset ring-white/20 hover:from-blue-500 hover:to-blue-700 active:from-blue-700 active:to-blue-800",
        success:
          "text-white [text-shadow:0_1px_0_theme(colors.emerald.900)] bg-gradient-to-b from-emerald-600 to-emerald-700 shadow-md shadow-zinc-950/20 ring-1 ring-inset ring-white/20 hover:from-emerald-500 hover:to-emerald-700 active:from-emerald-700 active:to-emerald-800",
        warning:
          "text-white [text-shadow:0_1px_0_theme(colors.amber.900)] bg-gradient-to-b from-amber-500 to-amber-600 shadow-md shadow-zinc-950/20 ring-1 ring-inset ring-white/20 hover:from-amber-400 hover:to-amber-600 active:from-amber-600 active:to-amber-700",
        destructive:
          "text-white bg-gradient-to-b from-destructive to-red-700 shadow-md shadow-zinc-950/20 ring-1 ring-inset ring-white/20 hover:from-red-500 hover:to-red-700 active:from-red-700 active:to-red-800",
        raised:
          "[text-shadow:0_1px_0_var(--color-zinc-100)] dark:[text-shadow:0_1px_0_var(--color-zinc-900)] bg-background hover:bg-zinc-50 dark:hover:bg-neutral-900 border-input/50 relative border-b-2 shadow-sm shadow-zinc-950/15 ring-0 ring-zinc-300 dark:ring-zinc-700 text-foreground",
        link:
          "text-primary underline-offset-4 relative after:absolute after:bottom-0 after:left-0 after:h-[1px] after:w-0 after:bg-current hover:after:w-full after:transition-[width] after:duration-150 !px-0 !pb-0 [&_svg]:text-muted-foreground group [&_svg]:group-hover:text-foreground transition-colors",
      },
      size: {
        default:
          "h-7 gap-1 px-2 text-xs/relaxed has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3.5",
        xs: "h-5 gap-1 rounded-sm px-2 text-[0.625rem] has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-2.5",
        sm: "h-6 gap-1 px-2 text-xs/relaxed has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&_svg:not([class*='size-'])]:size-3",
        lg: "h-8 gap-1 px-2.5 text-xs/relaxed has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2 [&_svg:not([class*='size-'])]:size-4",
        icon: "size-7 [&_svg:not([class*='size-'])]:size-3.5",
        "icon-xs": "size-5 rounded-sm [&_svg:not([class*='size-'])]:size-2.5",
        "icon-sm": "size-6 [&_svg:not([class*='size-'])]:size-3",
        "icon-lg": "size-8 [&_svg:not([class*='size-'])]:size-4",
      },
      animation: {
        all: "active:scale-[0.97] transition-all duration-150",
        colors: "transition-colors duration-150",
        none: "",
        "only-scale": "active:scale-[0.97] transition-scale duration-150",
      },
    },
    defaultVariants: {
      variant: "info",
      size: "default",
      animation: "all",
    },
  },
);

type ButtonProps = React.ComponentPropsWithoutRef<typeof ButtonPrimitive> &
  VariantProps<typeof buttonVariants> & {
    animation?: "all" | "colors" | "none" | "only-scale";
  };

const Button = React.forwardRef<React.ElementRef<typeof ButtonPrimitive>, ButtonProps>(
  (
    {
      className,
      variant = "info",
      size = "default",
      animation = "all",
      children,
      ...props
    },
    ref,
  ) => {
    return (
      <ButtonPrimitive
        ref={ref}
        data-slot="button"
        className={cn(
          buttonVariants({ variant, size, animation, className }),
          variant === "decorations" &&
            "relative rounded-none squircle-none overflow-visible",
        )}
        {...props}
      >
        {children}
        {variant === "decorations" && (
          <div className={cn("absolute -left-px -top-px z-10")}>
            <div className="relative">
              <div className="bg-muted-foreground w-px h-1.25 rounded-full absolute top-0" />
              <div className="bg-muted-foreground w-1.25 h-px rounded-full absolute left-0" />
            </div>
          </div>
        )}

        {variant === "decorations" && (
          <div className={cn("absolute right-0 -top-px z-10")}>
            <div className="relative">
              <div className="bg-muted-foreground w-px h-1.25 rounded-full absolute top-0" />
              <div className="bg-muted-foreground w-1.25 h-px rounded-full absolute -left-[4.5px]" />
            </div>
          </div>
        )}

        {variant === "decorations" && (
          <div className={cn("absolute -left-px bottom-0 z-10")}>
            <div className="relative">
              <div className="bg-muted-foreground w-px h-1.25 rounded-full absolute -top-[4.5px]" />
              <div className="bg-muted-foreground w-1.25 h-px rounded-full absolute left-0" />
            </div>
          </div>
        )}

        {variant === "decorations" && (
          <div className={cn("absolute right-0 bottom-0 z-10")}>
            <div className="relative">
              <div className="bg-muted-foreground w-px h-1.25 rounded-full absolute -top-[4.5px]" />
              <div className="bg-muted-foreground w-1.25 h-px rounded-full absolute -left-[4.5px]" />
            </div>
          </div>
        )}
      </ButtonPrimitive>
    );
  },
);

Button.displayName = "Button";

export { Button, buttonVariants };
