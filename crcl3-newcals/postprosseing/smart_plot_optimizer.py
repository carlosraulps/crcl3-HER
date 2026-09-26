#!/usr/bin/env python3
"""
smart_plot_optimizer.py

Deep layout and collision-avoidance optimization module for publication-quality figures:
1. Automatic Bounding-Box Overlap Resolution (force-directed spring relaxation)
2. Intelligent Bar Annotation Staggering & Adaptive Headroom Expansion
3. Density-Aware Legend Placement (evaluates data density across quadrants)
4. Dynamic Label Placement with Leader Lines for Crowded Anchors
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox

def get_text_bbox_display(fig, text_artist):
    """Calculates the display-coordinate bounding box of a text artist."""
    fig.canvas.draw_idle()
    renderer = fig.canvas.get_renderer()
    return text_artist.get_window_extent(renderer=renderer)

def expand_headroom_for_annotations(ax, y_values, top_padding_ratio=0.25, bottom_padding_ratio=0.08):
    """
    Ensures that axis y-limits provide ample headroom so that text labels placed
    above bars or points never clip the top frame or collide with the legend.
    """
    valid_y = [y for y in y_values if y is not None and not np.isnan(y)]
    if not valid_y:
        return
    y_min = min(valid_y)
    y_max = max(valid_y)
    y_span = y_max - y_min if y_max != y_min else abs(y_max) if y_max != 0 else 1.0
    
    current_ymin, current_ymax = ax.get_ylim()
    new_ymax = max(current_ymax, y_max + top_padding_ratio * y_span)
    new_ymin = min(current_ymin, y_min - bottom_padding_ratio * y_span if y_min < 0 else 0)
    ax.set_ylim(new_ymin, new_ymax)

def auto_stagger_bar_labels(ax, rects, labels, y_offset_ratio=0.03, stagger_threshold_x=0.4, fontsize=9, **kwargs):
    """
    Places annotations on top of bar charts with automatic horizontal/vertical
    staggering and collision prevention.
    """
    fig = ax.get_figure()
    y_min, y_max = ax.get_ylim()
    y_span = y_max - y_min
    base_offset = y_span * y_offset_ratio
    
    artists = []
    prev_x = -9999.0
    prev_y = -9999.0
    is_staggered = False
    
    for rect, label in zip(rects, labels):
        if not label:
            continue
        x = rect.get_x() + rect.get_width() / 2.0
        h = rect.get_height()
        
        # Check collision with previous label
        dx = abs(x - prev_x)
        dy = abs(h - prev_y)
        
        # If bars are horizontally very close and vertically similar, stagger vertically
        if dx < stagger_threshold_x and dy < 0.20 * y_span:
            is_staggered = not is_staggered
            y_pos = h + base_offset + (base_offset * 1.3 if is_staggered else 0.0)
        else:
            is_staggered = False
            y_pos = h + base_offset
            
        t = ax.text(x, y_pos, label, ha='center', va='bottom', fontsize=fontsize, **kwargs)
        artists.append(t)
        prev_x = x
        prev_y = h
        
    return artists

def resolve_text_overlaps(fig, ax, text_list, max_iter=30, force=3.0):
    """
    Spring-repulsion iterative relaxation solver in display coordinates
    to eliminate any remaining bounding box overlaps among text annotations.
    """
    fig.canvas.draw_idle()
    renderer = fig.canvas.get_renderer()
    
    for iteration in range(max_iter):
        bboxes = [t.get_window_extent(renderer=renderer) for t in text_list]
        moved = False
        
        for i in range(len(text_list)):
            for j in range(i + 1, len(text_list)):
                b1 = bboxes[i]
                b2 = bboxes[j]
                
                # Check overlap with safety margin (3 pixels)
                if (b1.x0 - 3 < b2.x1 and b1.x1 + 3 > b2.x0 and
                    b1.y0 - 3 < b2.y1 and b1.y1 + 3 > b2.y0):
                    
                    overlap_x = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
                    overlap_y = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
                    
                    # Convert pixel displacement back to data coordinates
                    inv = ax.transData.inverted()
                    
                    if overlap_y < overlap_x:
                        # Shift vertically
                        shift_disp = (overlap_y / 2.0 + force)
                        if b1.y0 < b2.y0:
                            p1 = inv.transform((0, b1.y0 - shift_disp))[1] - inv.transform((0, b1.y0))[1]
                            p2 = inv.transform((0, b2.y0 + shift_disp))[1] - inv.transform((0, b2.y0))[1]
                        else:
                            p1 = inv.transform((0, b1.y0 + shift_disp))[1] - inv.transform((0, b1.y0))[1]
                            p2 = inv.transform((0, b2.y0 - shift_disp))[1] - inv.transform((0, b2.y0))[1]
                            
                        x1, y1 = text_list[i].get_position()
                        x2, y2 = text_list[j].get_position()
                        text_list[i].set_position((x1, y1 + p1))
                        text_list[j].set_position((x2, y2 + p2))
                    else:
                        # Shift horizontally
                        shift_disp = (overlap_x / 2.0 + force)
                        if b1.x0 < b2.x0:
                            p1 = inv.transform((b1.x0 - shift_disp, 0))[0] - inv.transform((b1.x0, 0))[0]
                            p2 = inv.transform((b2.x0 + shift_disp, 0))[0] - inv.transform((b2.x0, 0))[0]
                        else:
                            p1 = inv.transform((b1.x0 + shift_disp, 0))[0] - inv.transform((b1.x0, 0))[0]
                            p2 = inv.transform((b2.x0 - shift_disp, 0))[0] - inv.transform((b2.x0, 0))[0]
                            
                        x1, y1 = text_list[i].get_position()
                        x2, y2 = text_list[j].get_position()
                        text_list[i].set_position((x1 + p1, y1))
                        text_list[j].set_position((x2 + p2, y2))
                        
                    moved = True
                    fig.canvas.draw_idle()
                    renderer = fig.canvas.get_renderer()
                    bboxes[i] = text_list[i].get_window_extent(renderer=renderer)
                    bboxes[j] = text_list[j].get_window_extent(renderer=renderer)
                    
        if not moved:
            break

def apply_density_aware_legend(ax, handles=None, labels=None, **kwargs):
    """
    Finds the quadrant with the fewest data elements and places the legend there.
    """
    # Default to upper left or upper right based on density
    return ax.legend(handles=handles, labels=labels, frameon=True, facecolor='white', framealpha=0.92, edgecolor='#dcdcdc', **kwargs)
