#!/usr/bin/env python3
"""Apply Parvaz branding and automatic best-server selection to v2rayNG."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NoReturn


APP_NAME = "Parvaz"
APPLICATION_ID = "com.parvaz.vpn"

SUBSCRIPTIONS = (
    (
        "Parvaz Collector Lite",
        "https://raw.githubusercontent.com/Kolandone/"
        "v2raycollector/main/config_lite.txt",
    ),
    (
        "Parvaz VLESS",
        "https://raw.githubusercontent.com/Argh94/"
        "V2RayAutoConfig/main/Vless.txt",
    ),
)


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Required file not found: {path}")

    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        text,
        encoding="utf-8",
    )


def replace_once(
    text: str,
    old: str,
    new: str,
    label: str,
) -> str:
    if old not in text:
        fail(
            f"Could not patch {label}: "
            "expected source text was not found"
        )

    return text.replace(
        old,
        new,
        1,
    )


def regex_once(
    text: str,
    pattern: str,
    replacement: str,
    label: str,
) -> str:
    result, count = re.subn(
        pattern,
        replacement,
        text,
        count=1,
        flags=re.DOTALL | re.MULTILINE,
    )

    if count != 1:
        fail(
            f"Could not patch {label}: "
            "source structure has changed"
        )

    return result


def patch_gradle(root: Path) -> None:
    path = (
        root
        / "V2rayNG/app/build.gradle.kts"
    )

    text = read(path)

    text = replace_once(
        text,
        'applicationId = "com.v2ray.ang"',
        f'applicationId = "{APPLICATION_ID}"',
        "applicationId",
    )

    count = text.count(
        'output.outputFileName = "v2rayNG_'
    )

    if count < 1:
        fail(
            "Could not patch APK filenames"
        )

    text = text.replace(
        'output.outputFileName = "v2rayNG_',
        'output.outputFileName = "Parvaz_',
    )

    write(path, text)


def patch_strings(root: Path) -> None:
    res = (
        root
        / "V2rayNG/app/src/main/res"
    )

    pattern = re.compile(
        r'(<string\s+name="app_name"'
        r'[^>]*>)'
        r'(.*?)'
        r'(</string>)'
    )

    found = False

    for path in res.glob(
        "values*/strings.xml"
    ):
        text = read(path)

        if not pattern.search(text):
            continue

        found = True

        text = pattern.sub(
            rf"\g<1>{APP_NAME}\g<3>",
            text,
            count=1,
        )

        write(path, text)

    if not found:
        fail(
            "No app_name string resource "
            "was found"
        )


def patch_theme(root: Path) -> None:
    path = (
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/compose/Theme.kt"
    )

    text = read(path)

    color_blocks = """
private val LightColor = lightColorScheme(
    primary = Color(0xFFFF6B35),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFFFDCCF),
    onPrimaryContainer = Color(0xFF351000),
    secondary = Color(0xFFF72585),
    onSecondary = Color(0xFFFFFFFF),
    tertiary = Color(0xFF7209B7),
    onTertiary = Color(0xFFFFFFFF),
    background = Color(0xFFFFF8F6),
    onBackground = Color(0xFF241A18),
    surface = Color(0xFFFFF8F6),
    onSurface = Color(0xFF241A18),
)

private val DarkColor = darkColorScheme(
    primary = Color(0xFFFF6B35),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFF7209B7),
    onPrimaryContainer = Color(0xFFFFFFFF),
    secondary = Color(0xFFF72585),
    onSecondary = Color(0xFFFFFFFF),
    tertiary = Color(0xFFD9B9FF),
    onTertiary = Color(0xFF43006D),
    background = Color(0xFF12121F),
    onBackground = Color(0xFFF0ECF4),
    surface = Color(0xFF12121F),
    onSurface = Color(0xFFF0ECF4),
    surfaceVariant = Color(0xFF343342),
    onSurfaceVariant = Color(0xFFD0CAD8),
)
""".lstrip()

    text = regex_once(
        text,
        r"private val LightColor = "
        r"lightColorScheme\(.*?^\)\s*"
        r"private val DarkColor = "
        r"darkColorScheme\(.*?^\)\s*",
        color_blocks,
        "Compose color schemes",
    )

    semantic_colors = {
        (
            "val colorPingRed = "
            "Color(0xFFFF0099)"
        ): (
            "val colorPingRed = "
            "Color(0xFFF72585)"
        ),
        (
            "val colorConfigType = "
            "Color(0xFFf97910)"
        ): (
            "val colorConfigType = "
            "Color(0xFFF72585)"
        ),
        (
            "val colorFabActive = "
            "Color(0xFFf97910)"
        ): (
            "val colorFabActive = "
            "Color(0xFFFF6B35)"
        ),
        (
            "val dividerColorDark = "
            "Color(0xFF424242)"
        ): (
            "val dividerColorDark = "
            "Color(0xFF343342)"
        ),
    }

    for old, new in semantic_colors.items():
        if old not in text:
            fail(
                "Could not patch theme color: "
                f"{old}"
            )

        text = text.replace(
            old,
            new,
            1,
        )

    write(path, text)

    write(
        root
        / "V2rayNG/app/src/main/res/"
        "values/parvaz_colors.xml",
        """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">#FF6B35</color>
    <color name="colorPrimaryDark">#7209B7</color>
    <color name="colorAccent">#F72585</color>
    <color name="colorBackground">#12121F</color>
</resources>
""",
    )


def patch_application(root: Path) -> None:
    path = (
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/AngApplication.kt"
    )

    text = read(path)

    text = replace_once(
        text,
        "        MMKV.initialize(this)\n",
        (
            "        MMKV.initialize(this)\n"
            "        ensureParvazDefaults()\n"
        ),
        "application defaults initialization",
    )

    text = replace_once(
        text,
        (
            "        // Initialize theme state "
            "from MMKV\n"
            "        ThemeManager.refresh()"
        ),
        """        // Default to dark mode only on the first launch.
        if (!com.v2ray.ang.handler.MmkvManager.decodeSettingsBool("parvaz_defaults_initialized")) {
            ThemeManager.setThemeMode("2")
            com.v2ray.ang.handler.MmkvManager.encodeSettings(
                "parvaz_defaults_initialized",
                true
            )
        } else {
            ThemeManager.refresh()
        }""",
        "default dark mode",
    )

    defaults = ",\n".join(
        (
            f'            "{name}" '
            f'to "{url}"'
        )
        for name, url in SUBSCRIPTIONS
    )

    method = f"""

    private fun ensureParvazDefaults() {{
        val defaults = listOf(
{defaults}
        )

        val existingUrls =
            com.v2ray.ang.handler.MmkvManager
                .decodeSubscriptions()
                .map {{ it.subscription.url }}
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
    }}
"""

    closing = text.rfind("\n}")

    if closing < 0:
        fail(
            "Could not locate "
            "AngApplication closing brace"
        )

    text = (
        text[:closing]
        + method
        + text[closing:]
    )

    write(path, text)


def patch_auto_selection(
    root: Path,
) -> None:
    view_model_path = (
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/main/"
        "MainViewModel.kt"
    )

    view_model = read(
        view_model_path
    )

    view_model = replace_once(
        view_model,
        """    @Volatile
    private var testingGroupId: String? = null

    private val initialPageReady""",
        """    @Volatile
    private var testingGroupId: String? = null

    private val pendingParvazTestGroups =
        java.util.ArrayDeque<String>()

    private var parvazTestingOnlyTcp: Boolean = false
    private var bestParvazServer: ServersCache? = null
    private var parvazTestWatchdog: Job? = null

    private val initialPageReady""",
        "Parvaz testing fields",
    )

    view_model = replace_once(
        view_model,
        """                dataSource.initAssets()
                dataSource.syncSubscriptions()""",
        """                dataSource.initAssets()
                dataSource.syncSubscriptions()
                dataSource.updateConfigViaSubAll()
                setupGroupTab(forceRefresh = true).join()
                delay(250L)
                testAllRealPing()""",
        "startup subscription update",
    )

    testing_block = """    fun cancelAllPing() {
        dataSource.cancelAllPing()
        pendingParvazTestGroups.clear()
        bestParvazServer = null
        testingGroupId = null

        parvazTestWatchdog?.cancel()
        parvazTestWatchdog = null

        _uiState.update {
            it.copy(
                isTesting = false,
                statusText = if (it.isRunning) {
                    connectedText
                } else {
                    disconnectedText
                }
            )
        }
    }

    fun testAllRealPing(
        onlyTcp: Boolean = false
    ) {
        dataSource.cancelAllPing()
        pendingParvazTestGroups.clear()

        bestParvazServer = null
        testingGroupId = null
        parvazTestingOnlyTcp = onlyTcp

        parvazTestWatchdog?.cancel()

        _uiState.update {
            it.copy(
                isTesting = true,
                statusText = dataSource.getString(
                    R.string.connection_test_testing
                )
            )
        }

        viewModelScope.launch(
            ioDispatcher
        ) {
            _uiState.value.groups.forEach {
                group ->

                if (
                    loadGroup(
                        group.id
                    ).isNotEmpty()
                ) {
                    pendingParvazTestGroups
                        .addLast(
                            group.id
                        )
                }
            }

            if (
                pendingParvazTestGroups
                    .isEmpty()
            ) {
                _uiState.update {
                    it.copy(
                        isTesting = false,
                        statusText =
                            disconnectedText
                    )
                }

                return@launch
            }

            startNextParvazGroupTest()
        }

        parvazTestWatchdog =
            viewModelScope.launch {
                delay(
                    300_000L
                )

                if (
                    _uiState.value.isTesting
                ) {
                    cancelAllPing()
                }
            }
    }

    private suspend fun startNextParvazGroupTest() {
        val groupId =
            pendingParvazTestGroups
                .pollFirst()

        if (groupId == null) {
            finishParvazTesting()
            return
        }

        val servers =
            loadGroup(groupId)

        testingGroupId = groupId

        dataSource
            .clearAllTestDelayResults(
                servers.map {
                    it.guid
                }
            )

        cacheMutex.withLock {
            groupDataCache.remove(
                groupId
            )
        }

        dataSource.sendMsg2TestService(
            TestServiceMessage(
                key =
                    AppConfig
                        .MSG_MEASURE_CONFIG_START,
                subscriptionId =
                    groupId,
                serverGuids =
                    emptyList(),
                onlyTcp =
                    parvazTestingOnlyTcp
            )
        )
    }

    fun testCurrentServerRealPing() {"""

    view_model = regex_once(
        view_model,
        (
            r"    fun cancelAllPing\(\) "
            r"\{.*?"
            r"    fun "
            r"testCurrentServerRealPing"
            r"\(\) \{"
        ),
        testing_block,
        "multi-group delay testing",
    )

    finish_block = """    private fun onTestsFinished() {
        val completedGroupId =
            testingGroupId ?: return

        viewModelScope.launch(
            ioDispatcher
        ) {
            cacheMutex.withLock {
                groupDataCache.remove(
                    completedGroupId
                )
            }

            val testedServers =
                loadGroup(
                    completedGroupId,
                    forceRefresh = true
                )

            updateGroupUi(
                completedGroupId,
                testedServers
            )

            val groupBest =
                testedServers
                    .asSequence()
                    .filter {
                        it.testDelayMillis > 0L
                    }
                    .minWithOrNull(
                        compareBy<ServersCache> {
                            it.testDelayMillis
                        }.thenBy {
                            it.profile.remarks
                        }
                    )

            if (groupBest != null) {
                val previous =
                    bestParvazServer

                if (
                    previous == null
                    || groupBest.testDelayMillis
                    < previous.testDelayMillis
                    || (
                        groupBest.testDelayMillis
                        == previous.testDelayMillis
                        && groupBest
                            .profile
                            .remarks
                        < previous
                            .profile
                            .remarks
                    )
                ) {
                    bestParvazServer =
                        groupBest

                    selectBestParvazServer(
                        groupBest
                    )
                }
            }

            if (
                pendingParvazTestGroups
                    .isNotEmpty()
            ) {
                startNextParvazGroupTest()
            } else {
                finishParvazTesting()
            }
        }
    }

    private fun selectBestParvazServer(
        server: ServersCache
    ) {
        dataSource.setSelectServer(
            server.guid
        )

        dataSource
            .setSelectedSubscriptionId(
                server
                    .profile
                    .subscriptionId
            )

        _uiState.update {
            it.copy(
                selectedGroupId =
                    server
                        .profile
                        .subscriptionId,
                selectedGuid =
                    server.guid
            )
        }
    }

    private fun finishParvazTesting() {
        bestParvazServer?.let {
            selectBestParvazServer(
                it
            )
        }

        testingGroupId = null
        pendingParvazTestGroups.clear()

        parvazTestWatchdog?.cancel()
        parvazTestWatchdog = null

        _uiState.update {
            it.copy(
                isTesting = false,
                statusText =
                    if (it.isRunning) {
                        connectedText
                    } else {
                        disconnectedText
                    }
            )
        }

        reloadAllGroups(
            _uiState.value.groups.map {
                it.id
            }
        )
    }

    fun triggerLocateSelectedServer() {"""

    view_model = regex_once(
        view_model,
        (
            r"    private fun "
            r"onTestsFinished\(\) "
            r"\{.*?"
            r"    fun "
            r"triggerLocateSelectedServer"
            r"\(\) \{"
        ),
        finish_block,
        "automatic best-server selection",
    )

    write(
        view_model_path,
        view_model,
    )

    activity_path = (
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/main/"
        "MainActivity.kt"
    )

    activity = read(
        activity_path
    )

    fab_block = """    private fun handleFabAction() {
        if (
            mainViewModel
                .uiState
                .value
                .isRunning
        ) {
            LauncherManager.stopService(
                this
            )

            return
        }

        lifecycleScope.launch {
            if (
                !mainViewModel
                    .uiState
                    .value
                    .isTesting
            ) {
                mainViewModel
                    .testAllRealPing()
            }

            val completed =
                kotlinx.coroutines
                    .withTimeoutOrNull(
                        300_000L
                    ) {
                        while (
                            mainViewModel
                                .uiState
                                .value
                                .isTesting
                        ) {
                            kotlinx.coroutines
                                .delay(
                                    250L
                                )
                        }

                        true
                    } ?: false

            if (!completed) {
                mainViewModel
                    .cancelAllPing()
            }

            if (
                SettingsManager
                    .isVpnMode()
            ) {
                val intent =
                    VpnService.prepare(
                        this@MainActivity
                    )

                if (intent == null) {
                    startV2Ray()
                } else {
                    requestVpnPermission
                        .launch(
                            intent
                        )
                }
            } else {
                startV2Ray()
            }
        }
    }

    private fun handleLayoutTestClick() {"""

    activity = regex_once(
        activity,
        (
            r"    private fun "
            r"handleFabAction\(\) "
            r"\{.*?"
            r"    private fun "
            r"handleLayoutTestClick"
            r"\(\) \{"
        ),
        fab_block,
        "Connect button automation",
    )

    write(
        activity_path,
        activity,
    )


def generate_icons(root: Path) -> None:
    try:
        from PIL import (
            Image,
            ImageDraw,
        )
    except ImportError as error:
        raise RuntimeError(
            "Pillow is required to generate "
            "launcher icons"
        ) from error

    res = (
        root
        / "V2rayNG/app/src/main/res"
    )

    sizes = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    start = (
        255,
        107,
        53,
    )

    end = (
        114,
        9,
        183,
    )

    for folder, size in sizes.items():
        image = Image.new(
            "RGBA",
            (
                size,
                size,
            ),
            (
                18,
                18,
                31,
                255,
            ),
        )

        draw = ImageDraw.Draw(
            image,
            "RGBA",
        )

        segments = max(
            20,
            size // 2,
        )

        for index in range(
            segments
        ):
            amount_start = (
                index
                / segments
            )

            amount_end = (
                index + 1
            ) / segments

            color = tuple(
                round(
                    start[channel]
                    + (
                        end[channel]
                        - start[channel]
                    )
                    * amount_start
                )
                for channel in range(3)
            ) + (255,)

            x_start = size * (
                0.18
                + 0.56 * amount_start
            )

            x_end = size * (
                0.18
                + 0.56 * amount_end
            )

            top_start = size * (
                0.63
                - 0.43
                * (
                    amount_start
                    ** 0.72
                )
            )

            top_end = size * (
                0.63
                - 0.43
                * (
                    amount_end
                    ** 0.72
                )
            )

            bottom_start = size * (
                0.70
                - 0.17 * amount_start
            )

            bottom_end = size * (
                0.70
                - 0.17 * amount_end
            )

            draw.polygon(
                [
                    (
                        x_start,
                        top_start,
                    ),
                    (
                        x_end,
                        top_end,
                    ),
                    (
                        x_end,
                        bottom_end,
                    ),
                    (
                        x_start,
                        bottom_start,
                    ),
                ],
                fill=color,
            )

        draw.line(
            (
                size * 0.32,
                size * 0.66,
                size * 0.72,
                size * 0.34,
            ),
            fill=(
                255,
                255,
                255,
                220,
            ),
            width=max(
                2,
                size // 18,
            ),
        )

        for offset, length in (
            (
                0.0,
                0.31,
            ),
            (
                0.10,
                0.25,
            ),
            (
                0.20,
                0.19,
            ),
        ):
            y_position = size * (
                0.71 + offset
            )

            draw.line(
                (
                    size * 0.15,
                    y_position,
                    size * (
                        0.15 + length
                    ),
                    y_position,
                ),
                fill=(
                    247,
                    37,
                    133,
                    230,
                ),
                width=max(
                    1,
                    size // 24,
                ),
            )

        target = res / folder

        target.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(
            target
            / "ic_launcher.png",
            optimize=True,
        )

        mask = Image.new(
            "L",
            (
                size,
                size,
            ),
            0,
        )

        ImageDraw.Draw(
            mask
        ).ellipse(
            (
                0,
                0,
                size - 1,
                size - 1,
            ),
            fill=255,
        )

        round_image = Image.new(
            "RGBA",
            (
                size,
                size,
            ),
            (
                0,
                0,
                0,
                0,
            ),
        )

        round_image.paste(
            image,
            (
                0,
                0,
            ),
            mask,
        )

        round_image.save(
            target
            / "ic_launcher_round.png",
            optimize=True,
        )

    drawable = (
        res
        / "drawable"
    )

    write(
        drawable
        / "ic_parvaz_background.xml",
        """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android"
    android:shape="rectangle">

    <solid android:color="#12121F" />

</shape>
""",
    )

    write(
        drawable
        / "ic_parvaz_foreground.xml",
        """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:aapt="http://schemas.android.com/aapt"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">

    <path
        android:pathData="M22,68 C39,64 48,37 82,24 C68,45 58,66 31,76 Z">

        <aapt:attr name="android:fillColor">

            <gradient
                android:startX="22"
                android:startY="68"
                android:endX="82"
                android:endY="24"
                android:type="linear"
                android:startColor="#FF6B35"
                android:endColor="#7209B7" />

        </aapt:attr>

    </path>

    <path
        android:fillColor="#F72585"
        android:pathData="M18,78 L49,78 L49,83 L18,83 Z" />

    <path
        android:fillColor="#F72585"
        android:pathData="M22,87 L46,87 L46,91 L22,91 Z" />

    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M35,70 L76,35 L79,39 L38,74 Z" />

</vector>
""",
    )

    adaptive = (
        res
        / "mipmap-anydpi-v26"
    )

    for name in (
        "ic_launcher.xml",
        "ic_launcher_round.xml",
    ):
        write(
            adaptive / name,
            """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">

    <background
        android:drawable="@drawable/ic_parvaz_background" />

    <foreground
        android:drawable="@drawable/ic_parvaz_foreground" />

</adaptive-icon>
""",
        )


def validate(root: Path) -> None:
    gradle = read(
        root
        / "V2rayNG/app/build.gradle.kts"
    )

    if (
        f'applicationId = "{APPLICATION_ID}"'
        not in gradle
    ):
        fail(
            "applicationId validation failed"
        )

    if (
        'output.outputFileName = "Parvaz_'
        not in gradle
    ):
        fail(
            "APK filename validation failed"
        )

    strings = read(
        root
        / "V2rayNG/app/src/main/res/"
        "values/strings.xml"
    )

    if (
        f">{APP_NAME}</string>"
        not in strings
    ):
        fail(
            "app name validation failed"
        )

    theme = read(
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/compose/"
        "Theme.kt"
    )

    if (
        "background = "
        "Color(0xFF12121F)"
        not in theme
    ):
        fail(
            "dark theme validation failed"
        )

    application = read(
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/"
        "AngApplication.kt"
    )

    for _, url in SUBSCRIPTIONS:
        if url not in application:
            fail(
                "subscription validation "
                f"failed: {url}"
            )

    view_model = read(
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/main/"
        "MainViewModel.kt"
    )

    if (
        "pendingParvazTestGroups"
        not in view_model
        or
        "selectBestParvazServer"
        not in view_model
    ):
        fail(
            "automatic server selection "
            "validation failed"
        )

    activity = read(
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/main/"
        "MainActivity.kt"
    )

    if (
        "LauncherManager.stopService"
        not in activity
    ):
        fail(
            "service stop validation failed"
        )

    if (
        "withTimeoutOrNull("
        not in activity
    ):
        fail(
            "Connect automation "
            "validation failed"
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
        root
        / "V2rayNG"
    ).is_dir():
        fail(
            f"Not a v2rayNG checkout: {root}"
        )

    patch_gradle(root)
    patch_strings(root)
    patch_theme(root)
    patch_application(root)
    patch_auto_selection(root)
    generate_icons(root)
    validate(root)

    print(
        "Parvaz customization "
        "completed successfully."
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(
            main()
        )

    except Exception as error:
        print(
            f"ERROR: {error}",
            file=sys.stderr,
        )

        raise
