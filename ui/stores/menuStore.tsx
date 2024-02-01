import { create } from 'zustand'

export interface MenuState {
  menuOpen: boolean
  toggleMenu: () => void
  closeMenu: () => void
}

export const useMenuStore = create<MenuState>()((set) => ({
    menuOpen: false,

    closeMenu: () => set({ menuOpen: false }),

    toggleMenu: () => set((state) => ({ menuOpen: !state.menuOpen })),

}))
