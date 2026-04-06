declare module "@/components/optics/sidebar" {
	import * as React from "react";

	export interface SidebarContextValue {
		state: "expanded" | "collapsed";
		open: boolean;
		setOpen: (value: boolean | ((value: boolean) => boolean)) => void;
		isMobile: boolean;
		openMobile: boolean;
		setOpenMobile: React.Dispatch<React.SetStateAction<boolean>>;
		toggleSidebar: () => void;
	}

	export function useSidebar(): SidebarContextValue;

	export const Sidebar: React.ComponentType<any>;
	export const SidebarContent: React.ComponentType<any>;
	export const SidebarFooter: React.ComponentType<any>;
	export const SidebarGroup: React.ComponentType<any>;
	export const SidebarGroupAction: React.ComponentType<any>;
	export const SidebarGroupContent: React.ComponentType<any>;
	export const SidebarGroupLabel: React.ComponentType<any>;
	export const SidebarHeader: React.ComponentType<any>;
	export const SidebarInput: React.ComponentType<any>;
	export const SidebarInset: React.ComponentType<any>;
	export const SidebarMenu: React.ComponentType<any>;
	export const SidebarMenuAction: React.ComponentType<any>;
	export const SidebarMenuBadge: React.ComponentType<any>;
	export const SidebarMenuButton: React.ComponentType<any>;
	export const SidebarMenuItem: React.ComponentType<any>;
	export const SidebarMenuSkeleton: React.ComponentType<any>;
	export const SidebarMenuSub: React.ComponentType<any>;
	export const SidebarMenuSubButton: React.ComponentType<any>;
	export const SidebarMenuSubItem: React.ComponentType<any>;
	export const SidebarProvider: React.ComponentType<any>;
	export const SidebarRail: React.ComponentType<any>;
	export const SidebarSeparator: React.ComponentType<any>;
	export const SidebarTrigger: React.ComponentType<any>;
}