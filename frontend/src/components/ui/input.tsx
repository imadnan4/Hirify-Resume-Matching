import type * as React from "react";

import { Input as OpticsInput } from "@/components/optics/input";

export type InputProps = React.ComponentPropsWithoutRef<typeof OpticsInput>;

const Input = OpticsInput;

export { Input };
