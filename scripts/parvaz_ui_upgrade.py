#!/usr/bin/env python3
"""Upgrade the customized v2rayNG UI to the Parvaz dashboard and seed subscriptions once."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SUBSCRIPTIONS = (
    (
        "Parvaz Collector Lite",
        "https://raw.githubusercontent.com/Kolandone/v2raycollector/main/config_lite.txt",
    ),
    (
        "Parvaz VLESS",
        "https://raw.githubusercontent.com/Argh94/V2RayAutoConfig/main/Vless.txt",
    ),
)


MAIN_SCREEN = r'''package com.v2ray.ang.ui.main

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBars
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.v2ray.ang.dto.entities.ServersCache

private val ParvazBackground = Color(0xFF050A17)
private val ParvazSurface = Color(0xFF0C1629)
private val ParvazSurfaceHigh = Color(0xFF101F39)
private val ParvazBlue = Color(0xFF12BFFF)
private val ParvazCyan = Color(0xFF38F2DA)
private val ParvazPurple = Color(0xFF8A3FFC)
private val ParvazPink = Color(0xFFEA3CFF)
private val ParvazGreen = Color(0xFF25E69A)
private val ParvazText = Color(0xFFF2F7FF)
private val ParvazMuted = Color(0xFF8FA6C5)

private enum class ParvazTab(val title: String, val symbol: String) {
    HOME("خانه", "⌂"),
    SERVERS("سرورها", "▤"),
    STATS("آمار", "▥"),
    SETTINGS("تنظیمات", "⚙"),
}

@Composable
fun MainScreen(
    mainViewModel: MainViewModel,
    onAction: (MainAction) -> Unit,
    onNavigate: (String) -> Unit,
) {
    val uiState by mainViewModel.uiState.collectAsStateWithLifecycle()
    val isLoading by mainViewModel.isLoading.collectAsStateWithLifecycle()
    val servers by mainViewModel
        .serversForGroup(uiState.selectedGroupId)
        .collectAsStateWithLifecycle()

    val selectedServer = remember(servers, uiState.selectedGuid) {
        servers.firstOrNull { it.guid == uiState.selectedGuid }
            ?: servers.firstOrNull()
    }

    var selectedTab by rememberSaveable {
        mutableStateOf(ParvazTab.HOME)
    }

    androidx.compose.runtime.CompositionLocalProvider(
        LocalLayoutDirection provides LayoutDirection.Rtl
    ) {
        Scaffold(
            containerColor = Color.Transparent,
            contentWindowInsets = WindowInsets(0, 0, 0, 0),
            bottomBar = {
                ParvazNavigationBar(
                    selectedTab = selectedTab,
                    onSelected = { selectedTab = it },
                )
            },
        ) { padding ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        Brush.verticalGradient(
                            listOf(
                                ParvazBackground,
                                Color(0xFF071225),
                                Color(0xFF040812),
                            )
                        )
                    )
                    .padding(padding)
            ) {
                ParvazAmbientBackground()

                when (selectedTab) {
                    ParvazTab.HOME -> ParvazHome(
                        uiState = uiState,
                        selectedServer = selectedServer,
                        isLoading = isLoading,
                        onConnect = {
                            onAction(MainAction.ToggleService)
                        },
                        onUpdate = {
                            onAction(MainAction.UpdateSubscriptions)
                        },
                        onTest = {
                            onAction(MainAction.TestRealAllServers)
                        },
                        onOpenServers = {
                            selectedTab = ParvazTab.SERVERS
                        },
                        onOpenSettings = {
                            selectedTab = ParvazTab.SETTINGS
                        },
                    )

                    ParvazTab.SERVERS -> ParvazServers(
                        uiState = uiState,
                        servers = servers,
                        isLoading = isLoading,
                        onAction = onAction,
                    )

                    ParvazTab.STATS -> ParvazStats(
                        uiState = uiState,
                        server = selectedServer,
                    )

                    ParvazTab.SETTINGS -> ParvazSettings(
                        onNavigate = onNavigate,
                    )
                }
            }
        }
    }
}

@Composable
private fun ParvazAmbientBackground() {
    Canvas(modifier = Modifier.fillMaxSize()) {
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(
                    ParvazBlue.copy(alpha = 0.18f),
                    Color.Transparent,
                ),
                center = Offset(
                    size.width * 0.18f,
                    size.height * 0.14f,
                ),
                radius = size.minDimension * 0.55f,
            ),
            radius = size.minDimension * 0.55f,
            center = Offset(
                size.width * 0.18f,
                size.height * 0.14f,
            ),
        )

        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(
                    ParvazPurple.copy(alpha = 0.16f),
                    Color.Transparent,
                ),
                center = Offset(
                    size.width * 0.90f,
                    size.height * 0.55f,
                ),
                radius = size.minDimension * 0.62f,
            ),
            radius = size.minDimension * 0.62f,
            center = Offset(
                size.width * 0.90f,
                size.height * 0.55f,
            ),
        )
    }
}

@Composable
private fun ParvazHome(
    uiState: MainUiState,
    selectedServer: ServersCache?,
    isLoading: Boolean,
    onConnect: () -> Unit,
    onUpdate: () -> Unit,
    onTest: () -> Unit,
    onOpenServers: () -> Unit,
    onOpenSettings: () -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding =
            androidx.compose.foundation.layout.PaddingValues(
                start = 18.dp,
                top = WindowInsets.statusBars
                    .asPaddingValues()
                    .calculateTopPadding() + 10.dp,
                end = 18.dp,
                bottom = 28.dp,
            ),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            ParvazHeader(
                title = "Parvaz Connect",
                isLoading = isLoading,
                onMenu = onOpenSettings,
                onRefresh = onUpdate,
            )
        }

        item {
            Column(
                modifier = Modifier.fillMaxWidth(),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Spacer(Modifier.height(8.dp))

                Text(
                    text = "اتصال سریع، امن و هوشمند",
                    color = ParvazMuted,
                    style = MaterialTheme.typography.bodyMedium,
                )

                Spacer(Modifier.height(20.dp))

                ParvazPowerButton(
                    isRunning = uiState.isRunning,
                    isTesting = uiState.isTesting,
                    onClick = onConnect,
                )

                Spacer(Modifier.height(12.dp))

                Text(
                    text = when {
                        uiState.isTesting ->
                            "در حال انتخاب بهترین سرور"

                        uiState.isRunning ->
                            "اتصال برقرار است"

                        else ->
                            "برای اتصال لمس کنید"
                    },
                    color = if (uiState.isRunning) {
                        ParvazGreen
                    } else {
                        ParvazText
                    },
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }

        item {
            StatusCard(
                isRunning = uiState.isRunning,
                statusText = uiState.statusText,
            )
        }

        item {
            SelectedServerCard(
                server = selectedServer,
                onClick = onOpenServers,
            )
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement =
                    Arrangement.spacedBy(12.dp),
            ) {
                MetricCard(
                    modifier = Modifier.weight(1f),
                    title = "پینگ",
                    value = selectedServer
                        ?.testDelayString
                        ?.takeIf { it.isNotBlank() }
                        ?: "—",
                    accent = ParvazCyan,
                )

                MetricCard(
                    modifier = Modifier.weight(1f),
                    title = "پروتکل",
                    value = selectedServer
                        ?.profile
                        ?.configType
                        ?.name
                        ?: "—",
                    accent = ParvazPink,
                )
            }
        }

        item {
            ConnectionQualityCard(
                delay = selectedServer?.testDelayMillis ?: 0L,
            )
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement =
                    Arrangement.spacedBy(12.dp),
            ) {
                QuickActionCard(
                    modifier = Modifier.weight(1f),
                    symbol = "⌁",
                    title = "تست پینگ",
                    subtitle = "انتخاب سریع‌ترین",
                    accent = ParvazBlue,
                    onClick = onTest,
                )

                QuickActionCard(
                    modifier = Modifier.weight(1f),
                    symbol = "▤",
                    title = "انتخاب سرور",
                    subtitle = "مشاهده همه سرورها",
                    accent = ParvazPurple,
                    onClick = onOpenServers,
                )
            }
        }
    }
}

@Composable
private fun ParvazHeader(
    title: String,
    isLoading: Boolean,
    onMenu: () -> Unit,
    onRefresh: () -> Unit,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        RoundTextButton(
            symbol = "☰",
            onClick = onMenu,
        )

        Text(
            text = title,
            color = ParvazText,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold,
        )

        if (isLoading) {
            Box(
                modifier = Modifier.size(42.dp),
                contentAlignment = Alignment.Center,
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.size(22.dp),
                    strokeWidth = 2.dp,
                    color = ParvazCyan,
                )
            }
        } else {
            RoundTextButton(
                symbol = "↻",
                onClick = onRefresh,
            )
        }
    }
}

@Composable
private fun RoundTextButton(
    symbol: String,
    onClick: () -> Unit,
) {
    Box(
        modifier = Modifier
            .size(42.dp)
            .clip(CircleShape)
            .background(
                ParvazSurfaceHigh.copy(alpha = 0.86f)
            )
            .border(
                1.dp,
                ParvazBlue.copy(alpha = 0.24f),
                CircleShape,
            )
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = symbol,
            color = ParvazText,
            fontSize = 21.sp,
            fontWeight = FontWeight.Bold,
        )
    }
}

@Composable
private fun ParvazPowerButton(
    isRunning: Boolean,
    isTesting: Boolean,
    onClick: () -> Unit,
) {
    val scale by animateFloatAsState(
        targetValue = if (isRunning) 1.04f else 1f,
        label = "powerScale",
    )

    val centerColor by animateColorAsState(
        targetValue = if (isRunning) {
            Color(0xFF082D35)
        } else {
            Color(0xFF0A1427)
        },
        label = "powerColor",
    )

    Box(
        modifier = Modifier
            .size(220.dp)
            .graphicsLayer {
                scaleX = scale
                scaleY = scale
            },
        contentAlignment = Alignment.Center,
    ) {
        Box(
            modifier = Modifier
                .size(220.dp)
                .background(
                    Brush.radialGradient(
                        listOf(
                            (
                                if (isRunning) {
                                    ParvazGreen
                                } else {
                                    ParvazBlue
                                }
                            ).copy(alpha = 0.22f),
                            Color.Transparent,
                        )
                    ),
                    CircleShape,
                )
        )

        Box(
            modifier = Modifier
                .size(184.dp)
                .clip(CircleShape)
                .background(centerColor)
                .border(
                    BorderStroke(
                        4.dp,
                        Brush.sweepGradient(
                            listOf(
                                ParvazBlue,
                                ParvazCyan,
                                ParvazPurple,
                                ParvazPink,
                                ParvazBlue,
                            )
                        )
                    ),
                    CircleShape,
                )
                .clickable(onClick = onClick),
            contentAlignment = Alignment.Center,
        ) {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = if (isTesting) "…" else "⏻",
                    color = ParvazText,
                    fontSize = 54.sp,
                    fontWeight = FontWeight.Light,
                )

                Text(
                    text = if (isRunning) {
                        "قطع اتصال"
                    } else {
                        "وصل"
                    },
                    color = ParvazText,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                )
            }
        }
    }
}

@Composable
private fun StatusCard(
    isRunning: Boolean,
    statusText: String,
) {
    ParvazCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Column(
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "وضعیت اتصال",
                    color = ParvazMuted,
                    fontSize = 12.sp,
                )

                Text(
                    text = if (isRunning) {
                        "آماده و محافظت‌شده"
                    } else {
                        statusText.ifBlank { "قطع" }
                    },
                    color = ParvazText,
                    fontWeight = FontWeight.SemiBold,
                )
            }

            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(9.dp)
                        .background(
                            if (isRunning) {
                                ParvazGreen
                            } else {
                                Color(0xFFFF5A75)
                            },
                            CircleShape,
                        )
                )

                Spacer(Modifier.width(8.dp))

                Text(
                    text = if (isRunning) {
                        "متصل"
                    } else {
                        "غیرفعال"
                    },
                    color = if (isRunning) {
                        ParvazGreen
                    } else {
                        Color(0xFFFF7890)
                    },
                    fontWeight = FontWeight.Bold,
                )
            }
        }
    }
}

@Composable
private fun SelectedServerCard(
    server: ServersCache?,
    onClick: () -> Unit,
) {
    ParvazCard(onClick = onClick) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier
                    .size(46.dp)
                    .background(
                        Brush.linearGradient(
                            listOf(
                                ParvazBlue,
                                ParvazPurple,
                            )
                        ),
                        RoundedCornerShape(14.dp),
                    ),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = flagFor(
                        server?.profile?.remarks.orEmpty()
                    ),
                    fontSize = 23.sp,
                )
            }

            Spacer(Modifier.width(12.dp))

            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = "سرور انتخاب‌شده",
                    color = ParvazMuted,
                    fontSize = 12.sp,
                )

                Text(
                    text = server
                        ?.profile
                        ?.remarks
                        ?.ifBlank { "بدون نام" }
                        ?: "هنوز سروری انتخاب نشده",
                    color = ParvazText,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                )

                Text(
                    text = server?.profile?.server.orEmpty(),
                    color = ParvazMuted,
                    fontSize = 11.sp,
                    maxLines = 1,
                )
            }

            Text(
                text = "‹",
                color = ParvazBlue,
                fontSize = 30.sp,
            )
        }
    }
}

@Composable
private fun MetricCard(
    modifier: Modifier,
    title: String,
    value: String,
    accent: Color,
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor =
                ParvazSurface.copy(alpha = 0.92f)
        ),
        shape = RoundedCornerShape(18.dp),
        border = BorderStroke(
            1.dp,
            accent.copy(alpha = 0.26f),
        ),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = title,
                color = ParvazMuted,
                fontSize = 12.sp,
            )

            Text(
                text = value,
                color = accent,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                maxLines = 1,
            )
        }
    }
}

@Composable
private fun ConnectionQualityCard(
    delay: Long,
) {
    val points = qualityPoints(delay)

    ParvazCard {
        Text(
            text = "کیفیت اتصال بر پایه پینگ",
            color = ParvazText,
            fontWeight = FontWeight.Bold,
        )

        Spacer(Modifier.height(12.dp))

        Canvas(
            modifier = Modifier
                .fillMaxWidth()
                .height(104.dp)
        ) {
            for (index in 1..3) {
                val y = size.height * index / 4f

                drawLine(
                    color =
                        ParvazMuted.copy(alpha = 0.12f),
                    start = Offset(0f, y),
                    end = Offset(size.width, y),
                    strokeWidth = 1f,
                )
            }

            val path = Path()

            points.forEachIndexed { index, value ->
                val x =
                    size.width *
                        index /
                        (
                            points.lastIndex
                                .coerceAtLeast(1)
                        ).toFloat()

                val y =
                    size.height * (1f - value)

                if (index == 0) {
                    path.moveTo(x, y)
                } else {
                    path.lineTo(x, y)
                }
            }

            drawPath(
                path = path,
                brush = Brush.horizontalGradient(
                    listOf(
                        ParvazBlue,
                        ParvazPurple,
                        ParvazPink,
                    )
                ),
                style = Stroke(
                    width = 5f,
                    cap = StrokeCap.Round,
                ),
            )
        }

        Text(
            text = qualityText(delay),
            color = if (delay in 1..180) {
                ParvazGreen
            } else {
                ParvazMuted
            },
            fontSize = 12.sp,
        )
    }
}

@Composable
private fun QuickActionCard(
    modifier: Modifier,
    symbol: String,
    title: String,
    subtitle: String,
    accent: Color,
    onClick: () -> Unit,
) {
    Card(
        modifier = modifier.clickable(
            onClick = onClick
        ),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(
            containerColor =
                ParvazSurface.copy(alpha = 0.92f)
        ),
        border = BorderStroke(
            1.dp,
            accent.copy(alpha = 0.35f),
        ),
    ) {
        Column(
            modifier = Modifier.padding(15.dp),
            verticalArrangement = Arrangement.spacedBy(5.dp),
        ) {
            Text(
                text = symbol,
                color = accent,
                fontSize = 25.sp,
            )

            Text(
                text = title,
                color = ParvazText,
                fontWeight = FontWeight.Bold,
            )

            Text(
                text = subtitle,
                color = ParvazMuted,
                fontSize = 11.sp,
            )
        }
    }
}

@Composable
private fun ParvazServers(
    uiState: MainUiState,
    servers: List<ServersCache>,
    isLoading: Boolean,
    onAction: (MainAction) -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(
                top = WindowInsets.statusBars
                    .asPaddingValues()
                    .calculateTopPadding() + 12.dp,
            )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 18.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(
                text = "سرورها",
                color = ParvazText,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
            )

            RoundTextButton(
                symbol = if (isLoading) "…" else "↻",
                onClick = {
                    onAction(
                        MainAction.UpdateSubscriptions
                    )
                },
            )
        }

        Spacer(Modifier.height(12.dp))

        LazyRow(
            modifier = Modifier.fillMaxWidth(),
            contentPadding =
                androidx.compose.foundation.layout.PaddingValues(
                    horizontal = 18.dp
                ),
            horizontalArrangement =
                Arrangement.spacedBy(8.dp),
        ) {
            items(
                uiState.groups,
                key = { it.id },
            ) { group ->
                val selected =
                    group.id == uiState.selectedGroupId

                Surface(
                    modifier = Modifier.clickable {
                        onAction(
                            MainAction.SelectGroup(
                                group.id
                            )
                        )
                    },
                    shape = RoundedCornerShape(50),
                    color = if (selected) {
                        ParvazBlue.copy(alpha = 0.22f)
                    } else {
                        ParvazSurface
                    },
                    border = BorderStroke(
                        1.dp,
                        if (selected) {
                            ParvazBlue
                        } else {
                            ParvazMuted.copy(
                                alpha = 0.18f
                            )
                        },
                    ),
                ) {
                    Text(
                        text = group.remarks,
                        modifier = Modifier.padding(
                            horizontal = 14.dp,
                            vertical = 9.dp,
                        ),
                        color = if (selected) {
                            ParvazCyan
                        } else {
                            ParvazMuted
                        },
                        fontWeight = if (selected) {
                            FontWeight.Bold
                        } else {
                            FontWeight.Normal
                        },
                    )
                }
            }
        }

        Spacer(Modifier.height(12.dp))

        if (servers.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text =
                        "سروری در این گروه وجود ندارد",
                    color = ParvazMuted,
                )
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding =
                    androidx.compose.foundation.layout.PaddingValues(
                        start = 18.dp,
                        end = 18.dp,
                        bottom = 24.dp,
                    ),
                verticalArrangement =
                    Arrangement.spacedBy(10.dp),
            ) {
                items(
                    servers,
                    key = { it.guid },
                ) { server ->
                    ServerRow(
                        server = server,
                        selected =
                            server.guid ==
                                uiState.selectedGuid,
                        onClick = {
                            onAction(
                                MainAction.SelectServer(
                                    server.guid
                                )
                            )
                        },
                    )
                }
            }
        }
    }
}

@Composable
private fun ServerRow(
    server: ServersCache,
    selected: Boolean,
    onClick: () -> Unit,
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(17.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (selected) {
                Color(0xFF102B4B)
            } else {
                ParvazSurface.copy(alpha = 0.94f)
            }
        ),
        border = BorderStroke(
            1.dp,
            if (selected) {
                ParvazBlue
            } else {
                ParvazMuted.copy(alpha = 0.16f)
            },
        ),
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = flagFor(server.profile.remarks),
                fontSize = 25.sp,
            )

            Spacer(Modifier.width(12.dp))

            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = server
                        .profile
                        .remarks
                        .ifBlank { "بدون نام" },
                    color = ParvazText,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                )

                Text(
                    text = listOfNotNull(
                        server.profile.configType.name,
                        server.profile.server,
                    ).joinToString(" • "),
                    color = ParvazMuted,
                    fontSize = 11.sp,
                    maxLines = 1,
                )
            }

            Column(
                horizontalAlignment = Alignment.End
            ) {
                Text(
                    text = server
                        .testDelayString
                        .ifBlank { "—" },
                    color = delayColor(
                        server.testDelayMillis
                    ),
                    fontWeight = FontWeight.Bold,
                )

                Text(
                    text = if (selected) {
                        "فعال"
                    } else {
                        "انتخاب"
                    },
                    color = if (selected) {
                        ParvazGreen
                    } else {
                        ParvazMuted
                    },
                    fontSize = 10.sp,
                )
            }
        }
    }
}

@Composable
private fun ParvazStats(
    uiState: MainUiState,
    server: ServersCache?,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding =
            androidx.compose.foundation.layout.PaddingValues(
                start = 18.dp,
                top = WindowInsets.statusBars
                    .asPaddingValues()
                    .calculateTopPadding() + 16.dp,
                end = 18.dp,
                bottom = 24.dp,
            ),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item {
            Text(
                text = "آمار اتصال",
                color = ParvazText,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
            )
        }

        item {
            ConnectionQualityCard(
                delay = server?.testDelayMillis ?: 0L
            )
        }

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement =
                    Arrangement.spacedBy(12.dp),
            ) {
                MetricCard(
                    modifier = Modifier.weight(1f),
                    title = "وضعیت",
                    value = if (uiState.isRunning) {
                        "متصل"
                    } else {
                        "قطع"
                    },
                    accent = if (uiState.isRunning) {
                        ParvazGreen
                    } else {
                        Color(0xFFFF7890)
                    },
                )

                MetricCard(
                    modifier = Modifier.weight(1f),
                    title = "تاخیر",
                    value = server
                        ?.testDelayString
                        ?.ifBlank { "—" }
                        ?: "—",
                    accent = ParvazCyan,
                )
            }
        }

        item {
            ParvazCard {
                Text(
                    text = "سرور فعال",
                    color = ParvazMuted,
                    fontSize = 12.sp,
                )

                Spacer(Modifier.height(6.dp))

                Text(
                    text = server
                        ?.profile
                        ?.remarks
                        ?: "انتخاب نشده",
                    color = ParvazText,
                    fontWeight = FontWeight.Bold,
                )

                Text(
                    text = server
                        ?.profile
                        ?.getServerAddressAndPort()
                        .orEmpty(),
                    color = ParvazMuted,
                    fontSize = 12.sp,
                )
            }
        }

        item {
            ParvazCard {
                Text(
                    text = "سرعت دانلود و آپلود",
                    color = ParvazText,
                    fontWeight = FontWeight.Bold,
                )

                Spacer(Modifier.height(7.dp))

                Text(
                    text =
                        "نمایش سرعت زنده در نسخه بعدی با اتصال مستقیم به آمار Core اضافه می‌شود.",
                    color = ParvazMuted,
                    fontSize = 12.sp,
                    lineHeight = 19.sp,
                )
            }
        }
    }
}

@Composable
private fun ParvazSettings(
    onNavigate: (String) -> Unit,
) {
    val items = listOf(
        Triple(
            "اشتراک‌ها",
            "مدیریت منابع و به‌روزرسانی",
            "sub_setting",
        ),
        Triple(
            "تنظیمات عمومی",
            "حالت اتصال، تم و رفتار برنامه",
            "settings",
        ),
        Triple(
            "مسیریابی",
            "قوانین عبور ترافیک",
            "routing_setting",
        ),
        Triple(
            "برنامه‌های منتخب",
            "مدیریت پروکسی برای هر برنامه",
            "per_app_proxy",
        ),
        Triple(
            "پشتیبان‌گیری",
            "خروجی و بازیابی تنظیمات",
            "backup_restore",
        ),
        Triple(
            "درباره Parvaz",
            "نسخه و اطلاعات برنامه",
            "about",
        ),
    )

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding =
            androidx.compose.foundation.layout.PaddingValues(
                start = 18.dp,
                top = WindowInsets.statusBars
                    .asPaddingValues()
                    .calculateTopPadding() + 16.dp,
                end = 18.dp,
                bottom = 24.dp,
            ),
        verticalArrangement = Arrangement.spacedBy(11.dp),
    ) {
        item {
            Text(
                text = "تنظیمات",
                color = ParvazText,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
            )
        }

        item {
            ParvazCard {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment =
                        Alignment.CenterVertically,
                ) {
                    Box(
                        modifier = Modifier
                            .size(48.dp)
                            .background(
                                Brush.linearGradient(
                                    listOf(
                                        ParvazBlue,
                                        ParvazPurple,
                                    )
                                ),
                                RoundedCornerShape(15.dp),
                            ),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = "P",
                            color = Color.White,
                            fontSize = 24.sp,
                            fontWeight = FontWeight.Black,
                        )
                    }

                    Spacer(Modifier.width(12.dp))

                    Column {
                        Text(
                            text = "Parvaz Connect",
                            color = ParvazText,
                            fontWeight = FontWeight.Bold,
                        )

                        Text(
                            text =
                                "امن، سریع و بدون پیچیدگی",
                            color = ParvazMuted,
                            fontSize = 11.sp,
                        )
                    }
                }
            }
        }

        items(items) { item ->
            SettingsRow(
                title = item.first,
                subtitle = item.second,
                onClick = {
                    onNavigate(item.third)
                },
            )
        }
    }
}

@Composable
private fun SettingsRow(
    title: String,
    subtitle: String,
    onClick: () -> Unit,
) {
    ParvazCard(onClick = onClick) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier
                    .size(42.dp)
                    .background(
                        ParvazBlue.copy(alpha = 0.12f),
                        RoundedCornerShape(13.dp),
                    ),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = "◇",
                    color = ParvazCyan,
                    fontSize = 22.sp,
                )
            }

            Spacer(Modifier.width(12.dp))

            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = title,
                    color = ParvazText,
                    fontWeight = FontWeight.Bold,
                )

                Text(
                    text = subtitle,
                    color = ParvazMuted,
                    fontSize = 11.sp,
                )
            }

            Text(
                text = "‹",
                color = ParvazBlue,
                fontSize = 28.sp,
            )
        }
    }
}

@Composable
private fun ParvazNavigationBar(
    selectedTab: ParvazTab,
    onSelected: (ParvazTab) -> Unit,
) {
    NavigationBar(
        containerColor = Color(0xF20A1324),
        tonalElevation = 0.dp,
        windowInsets = WindowInsets.navigationBars,
    ) {
        ParvazTab.values().forEach { tab ->
            val selected = tab == selectedTab

            NavigationBarItem(
                selected = selected,
                onClick = {
                    onSelected(tab)
                },
                icon = {
                    Text(
                        text = tab.symbol,
                        color = if (selected) {
                            ParvazCyan
                        } else {
                            ParvazMuted
                        },
                        fontSize = 21.sp,
                        fontWeight = FontWeight.Bold,
                    )
                },
                label = {
                    Text(
                        text = tab.title,
                        color = if (selected) {
                            ParvazCyan
                        } else {
                            ParvazMuted
                        },
                        fontSize = 10.sp,
                    )
                },
                colors =
                    NavigationBarItemDefaults.colors(
                        indicatorColor =
                            ParvazBlue.copy(
                                alpha = 0.16f
                            ),
                    ),
            )
        }
    }
}

@Composable
private fun ParvazCard(
    onClick: (() -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit,
) {
    val modifier = if (onClick == null) {
        Modifier.fillMaxWidth()
    } else {
        Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    }

    Card(
        modifier = modifier,
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor =
                ParvazSurface.copy(alpha = 0.92f)
        ),
        border = BorderStroke(
            1.dp,
            ParvazBlue.copy(alpha = 0.16f),
        ),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            content = content,
        )
    }
}

private fun delayColor(delay: Long): Color = when {
    delay <= 0L ->
        ParvazMuted

    delay <= 180L ->
        ParvazGreen

    delay <= 350L ->
        Color(0xFFFFD66B)

    else ->
        Color(0xFFFF6B86)
}

private fun qualityText(delay: Long): String = when {
    delay <= 0L ->
        "برای ارزیابی کیفیت، تست پینگ را اجرا کنید."

    delay <= 120L ->
        "کیفیت عالی"

    delay <= 220L ->
        "کیفیت خوب"

    delay <= 400L ->
        "کیفیت متوسط"

    else ->
        "کیفیت ضعیف؛ سرور دیگری انتخاب کنید."
}

private fun qualityPoints(
    delay: Long
): List<Float> {
    val base = when {
        delay <= 0L -> 0.46f
        delay <= 120L -> 0.82f
        delay <= 220L -> 0.67f
        delay <= 400L -> 0.48f
        else -> 0.30f
    }

    return listOf(
        base * 0.72f,
        base * 0.88f,
        base * 0.80f,
        base,
        base * 0.84f,
        (base * 1.06f).coerceAtMost(0.96f),
        base * 0.90f,
        (base * 1.10f).coerceAtMost(0.98f),
        base * 0.94f,
    )
}

private fun flagFor(
    remarks: String
): String {
    val value = remarks.lowercase()

    return when {
        listOf(
            "germany",
            "de-",
            "frankfurt",
            "آلمان",
        ).any(value::contains) ->
            "🇩🇪"

        listOf(
            "france",
            "paris",
            "فرانسه",
        ).any(value::contains) ->
            "🇫🇷"

        listOf(
            "turkey",
            "istanbul",
            "ترکیه",
        ).any(value::contains) ->
            "🇹🇷"

        listOf(
            "netherlands",
            "amsterdam",
            "هلند",
        ).any(value::contains) ->
            "🇳🇱"

        listOf(
            "finland",
            "helsinki",
            "فنلاند",
        ).any(value::contains) ->
            "🇫🇮"

        listOf(
            "usa",
            "united states",
            "america",
            "آمریکا",
        ).any(value::contains) ->
            "🇺🇸"

        listOf(
            "uk",
            "london",
            "england",
            "انگلیس",
        ).any(value::contains) ->
            "🇬🇧"

        listOf(
            "canada",
            "toronto",
            "کانادا",
        ).any(value::contains) ->
            "🇨🇦"

        listOf(
            "singapore",
            "سنگاپور",
        ).any(value::contains) ->
            "🇸🇬"

        listOf(
            "japan",
            "tokyo",
            "ژاپن",
        ).any(value::contains) ->
            "🇯🇵"

        else ->
            "🌐"
    }
}
'''


def read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(
            f"Required file not found: {path}"
        )

    return path.read_text(
        encoding="utf-8"
    )


def write(
    path: Path,
    content: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        content,
        encoding="utf-8",
    )


def patch_subscription_seed(
    root: Path,
) -> None:
    path = (
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/AngApplication.kt"
    )

    text = read(path)

    text = re.sub(
        r"\n    private fun "
        r"(?:ensureParvazDefaults|"
        r"ensureParvazSubscriptions|"
        r"seedParvazSubscriptionsOnce)"
        r"\(\) \{.*?\n    \}\n(?=\})",
        "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )

    text = re.sub(
        r"\s+"
        r"(?:ensureParvazDefaults|"
        r"ensureParvazSubscriptions|"
        r"seedParvazSubscriptionsOnce)"
        r"\(\)",
        "\n        seedParvazSubscriptionsOnce()",
        text,
        count=1,
    )

    if (
        "seedParvazSubscriptionsOnce()"
        not in text
    ):
        marker = "        MMKV.initialize(this)"

        if marker not in text:
            raise RuntimeError(
                "MMKV initialization marker not found"
            )

        text = text.replace(
            marker,
            marker
            + "\n        seedParvazSubscriptionsOnce()",
            1,
        )

    defaults = ",\n".join(
        f'            "{name}" to "{url}"'
        for name, url in SUBSCRIPTIONS
    )

    method = f'''

    private fun seedParvazSubscriptionsOnce() {{
        val seedKey = "parvaz_subscriptions_seeded_v2"

        if (
            com.v2ray.ang.handler.MmkvManager
                .decodeSettingsBool(
                    seedKey,
                    false
                )
        ) return

        val defaults = listOf(
{defaults}
        )

        val existingUrls =
            com.v2ray.ang.handler.MmkvManager
                .decodeSubscriptions()
                .map {{
                    it.subscription.url
                }}
                .toSet()

        defaults.forEach {{ (remarks, url) ->
            if (url !in existingUrls) {{
                com.v2ray.ang.handler.MmkvManager
                    .encodeSubscription(
                        java.util.UUID
                            .randomUUID()
                            .toString(),
                        com.v2ray.ang.dto.entities
                            .SubscriptionItem(
                                remarks = remarks,
                                url = url,
                                enabled = true,
                                autoUpdate = true,
                                updateInterval = 1440
                            )
                    )
            }}
        }}

        com.v2ray.ang.handler.MmkvManager
            .encodeSettings(
                seedKey,
                true
            )
    }}
'''

    closing = text.rfind("\n}")

    if closing < 0:
        raise RuntimeError(
            "AngApplication closing brace not found"
        )

    text = (
        text[:closing]
        + method
        + text[closing:]
    )

    write(
        path,
        text,
    )


def install_ui(
    root: Path,
) -> None:
    path = (
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/main/MainScreen.kt"
    )

    write(
        path,
        MAIN_SCREEN,
    )


def validate(
    root: Path,
) -> None:
    app = read(
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/AngApplication.kt"
    )

    screen = read(
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/main/MainScreen.kt"
    )

    required_app = (
        "parvaz_subscriptions_seeded_v2",
        "seedParvazSubscriptionsOnce()",
    )

    required_screen = (
        "Parvaz Connect",
        "ParvazPowerButton",
        "ParvazServers",
        "ParvazSettings",
        "androidx.compose.ui.graphics.graphicsLayer",
    )

    for token in required_app:
        if token not in app:
            raise RuntimeError(
                "Application patch validation failed: "
                f"{token}"
            )

    for token in required_screen:
        if token not in screen:
            raise RuntimeError(
                "UI patch validation failed: "
                f"{token}"
            )


def main() -> int:
    if len(sys.argv) != 2:
        print(
            f"Usage: {sys.argv[0]} "
            "PATH_TO_V2RAYNG_CHECKOUT",
            file=sys.stderr,
        )

        return 2

    root = Path(
        sys.argv[1]
    ).resolve()

    if not (
        root / "V2rayNG"
    ).is_dir():
        raise RuntimeError(
            f"Not a v2rayNG checkout: {root}"
        )

    patch_subscription_seed(root)
    install_ui(root)
    validate(root)

    print(
        "Parvaz dashboard UI and "
        "one-time subscription seeding installed."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
