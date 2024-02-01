import { create } from 'zustand'

interface MenuState {
  menuOpen: boolean
  toggleMenu: () => void
  closeMenu: () => void
}

const useMenuStore = create<MenuState>()((set) => ({
    menuOpen: false,

    closeMenu: () => set({ menuOpen: false }),

    toggleMenu: () => set((state) => ({ menuOpen: !state.menuOpen })),

}))

export default useMenuStore