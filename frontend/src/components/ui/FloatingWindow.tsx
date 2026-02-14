
import { useState, useRef, type ReactNode } from 'react';
import { motion, useDragControls } from 'framer-motion';
import { Maximize2, Minimize2, X, GripHorizontal, Minus } from 'lucide-react';
import { ResizableBox, ResizeCallbackData } from 'react-resizable';
import { clsx } from 'clsx';
import 'react-resizable/css/styles.css';

interface FloatingWindowProps {
    id: string;
    title: string;
    isOpen: boolean;
    onClose: () => void;
    onFocus: () => void;
    initialPosition?: { x: number; y: number };
    initialSize?: { width: number; height: number };
    zIndex: number;
    children: ReactNode;
    minWidth?: number;
    minHeight?: number;
}

export const FloatingWindow = ({
    id,
    title,
    isOpen,
    onClose,
    onFocus,
    initialPosition = { x: 100, y: 100 },
    initialSize = { width: 400, height: 300 },
    zIndex,
    children,
    minWidth = 300,
    minHeight = 200
}: FloatingWindowProps) => {
    const [isMaximized, setIsMaximized] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [size, setSize] = useState(initialSize);
    const [isInteracting, setIsInteracting] = useState(false);

    // We use Framer Motion for dragging, but we need to sync with React Resizable
    // Since ResizableBox handles its own size state, we need to be careful.

    const dragControls = useDragControls();

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const windowRef = useRef<HTMLDivElement>(null);

    const handleResizeStart = () => setIsInteracting(true);
    const handleResizeStop = () => setIsInteracting(false);

    const handleResize = (e: any, data: ResizeCallbackData) => {
        setSize({ width: data.size.width, height: data.size.height });
    };

    if (!isOpen) return null;

    return (
        <motion.div
            drag={!isMaximized}
            dragListener={false}
            dragControls={dragControls}
            dragMomentum={false}
            onDragStart={() => setIsInteracting(true)}
            onDragEnd={() => setIsInteracting(false)}
            initial={initialPosition}
            style={{
                position: 'fixed',
                zIndex,
                // If maximized, we force fixed position 0,0 and full width/height
                ...(isMaximized ? { top: 0, left: 0, right: 0, bottom: 0, transform: 'none !important' } : {})
            }}
            className={clsx(
                "flex flex-col bg-[#0f1115] border border-white/10 rounded-lg shadow-2xl overflow-hidden backdrop-blur-md transition-shadow duration-200",
                isMaximized ? "w-screen h-screen rounded-none" : "",
                isMinimized ? "h-auto w-64" : "",
                isInteracting ? "shadow-[0_0_30px_rgba(255,255,255,0.1)] scale-[1.002]" : ""
            )}
            onMouseDown={onFocus}
        >
            {/* Header / Drag Handle */}
            <div
                className={clsx(
                    "h-9 bg-white/5 border-b border-white/5 flex items-center justify-between px-3 select-none group transition-colors",
                    isMaximized ? "" : "cursor-grab active:cursor-grabbing hover:bg-white/10"
                )}
                onPointerDown={(e) => {
                    if (!isMaximized) dragControls.start(e);
                }}
            >
                <div className="flex items-center gap-2">
                    <GripHorizontal className="w-4 h-4 text-white/20 group-hover:text-white/40 transition-colors" />
                    <span className="text-xs font-medium text-white/80 group-hover:text-white transition-colors">{title}</span>
                </div>

                {/* Window Controls */}
                <div className="flex items-center gap-1.5" onPointerDown={(e) => e.stopPropagation()}>
                    <button
                        onClick={() => setIsMinimized(!isMinimized)}
                        className="p-1 hover:bg-white/10 rounded transition-colors"
                        title="Minimize"
                    >
                        <Minus className="w-3 h-3 text-white/60 hover:text-white" />
                    </button>
                    <button
                        onClick={() => {
                            setIsMaximized(!isMaximized);
                            setIsMinimized(false);
                        }}
                        className="p-1 hover:bg-white/10 rounded transition-colors"
                        title={isMaximized ? "Restore" : "Maximize"}
                    >
                        {isMaximized ? (
                            <Minimize2 className="w-3 h-3 text-white/60 hover:text-white" />
                        ) : (
                            <Maximize2 className="w-3 h-3 text-white/60 hover:text-white" />
                        )}
                    </button>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-red-500/20 hover:text-red-400 rounded transition-colors"
                        title="Close"
                    >
                        <X className="w-3 h-3 text-white/60" />
                    </button>
                </div>
            </div>

            {/* Content Area */}
            {!isMinimized && (
                <div className={clsx("flex-1 relative overflow-hidden bg-black/40", isInteracting && "pointer-events-none")}>
                    {isMaximized ? (
                        <div className="w-full h-full overflow-auto custom-scrollbar">
                            {/* Overlay to catch events during drag even if not resized */}
                            {isInteracting && <div className="absolute inset-0 z-50 bg-transparent" />}
                            {children}
                        </div>
                    ) : (
                        <ResizableBox
                            width={size.width}
                            height={size.height}
                            minConstraints={[minWidth, minHeight]}
                            maxConstraints={[1920, 1080]}
                            onResizeStart={handleResizeStart}
                            onResizeStop={handleResizeStop}
                            onResize={handleResize}
                            resizeHandles={['se']}
                            className="relative"
                            handle={(
                                <div className="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize flex items-center justify-center opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity z-50">
                                    <div className="w-2 h-2 border-r-2 border-b-2 border-white/30" />
                                </div>
                            )}
                        >
                            <div className="w-full h-full overflow-auto custom-scrollbar" style={{ width: size.width, height: size.height }}>
                                {/* Overlay to catch events during drag/resize */}
                                {isInteracting && <div className="absolute inset-0 z-50 bg-transparent" />}
                                {children}
                            </div>
                        </ResizableBox>
                    )}
                </div>
            )}
        </motion.div>
    );
};
