import type * as React from "react";

import {
	Button as OpticsButton,
	buttonVariants as opticsButtonVariants,
} from "@/components/optics/button";

export type ButtonProps = React.ComponentPropsWithoutRef<typeof OpticsButton>;

const Button = OpticsButton;
const buttonVariants = opticsButtonVariants;

export { Button, buttonVariants };
