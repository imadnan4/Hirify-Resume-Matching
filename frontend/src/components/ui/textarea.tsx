import type * as React from "react";

import { Textarea as OpticsTextarea } from "@/components/optics/textarea";

export type TextareaProps = React.ComponentPropsWithoutRef<typeof OpticsTextarea>;

const Textarea = OpticsTextarea;

export { Textarea };
