#!/usr/bin/env python3
"""Apply Parvaz branding and automation to a checked-out v2rayNG tree."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable, NoReturn


APP_NAME = "Parvaz"
APPLICATION_ID = "com.parvaz.vpn"

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


def fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"Required file not found: {path}")

    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_required(
    text: str,
    old: str,
    new: str,
    label: str,
) -> str:
    if old not in text:
        fail(
            f"Could not patch {label}: "
            "expected text was not found"
        )

    return text.replace(old, new, 1)


def replace_regex_required(
    text: str,
    pattern: re.Pattern[str],
    replacement: str,
    label: str,
) -> str:
    result, count = pattern.subn(
        replacement,
        text,
        count=1,
    )

    if count != 1:
        fail(
            f"Could not patch {label}: "
            "source structure has changed"
        )

    return result


def patch_gradle(root: Path) -> None:
    path = root / "V2rayNG/app/build.gradle.kts"
    text = read(path)

    text = replace_required(
        text,
        'applicationId = "com.v2ray.ang"',
        f'applicationId = "{APPLICATION_ID}"',
        "applicationId",
    )

    text = text.replace(
        '"v2rayNG_${variant.versionName}',
        '"Parvaz_${variant.versionName',
    )

    if 'ndkVersion = "29.0.14206865"' not in text:
        text = replace_required(
            text,
            "android {",
            'android {\n    ndkVersion = "29.0.14206865"',
            "NDK version",
        )

    write(path, text)


def patch_strings(root: Path) -> None:
    res = root / "V2rayNG/app/src/main/res"
    found = False

    pattern = re.compile(
        r'(<string\s+name="app_name"[^>]*>)'
        r'(.*?)'
        r'(</string>)'
    )

    for path in res.glob("values*/strings.xml"):
        text = read(path)

        if pattern.search(text):
            found = True

            text = pattern.sub(
                rf"\g<1>{APP_NAME}\g<3>",
                text,
                count=1,
            )

            write(path, text)

    if not found:
        fail("No app_name resource was found")


def patch_compose_theme(root: Path) -> None:
    path = (
        root
        / "V2rayNG/app/src/main/java/com/v2ray/ang/"
        "ui/compose/Theme.kt"
    )

    text = read(path)

    schemes_pattern = re.compile(
        r"private val LightColor = lightColorScheme\("
        r".*?^\s*\)\s*"
        r"private val DarkColor = darkColorScheme\("
        r".*?^\s*\)\s*",
        re.DOTALL | re.MULTILINE,
    )

    schemes = """private val LightColor = lightColorScheme(
    primary = Color(0xFFFF6B35),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFFFDCCF),
    onPrimaryContainer = Color(0xFF351000),
    secondary = Color(0xFFF72585),
    onSecondary = Color(0xFFFFFFFF),
    secondaryContainer = Color(0xFFFFD8E8),
    onSecondaryContainer = Color(0xFF3D0020),
    tertiary = Color(0xFF7209B7),
    onTertiary = Color(0xFFFFFFFF),
    tertiaryContainer = Color(0xFFEEDBFF),
    onTertiaryContainer = Color(0xFF27003F),
    error = Color(0xFFBA1A1A),
    errorContainer = Color(0xFFFFDAD6),
    onError = Color(0xFFFFFFFF),
    onErrorContainer = Color(0xFF410002),
    background = Color(0xFFFFF8F6),
    onBackground = Color(0xFF241A18),
    surface = Color(0xFFFFF8F6),
    onSurface = Color(0xFF241A18),
    surfaceVariant = Color(0xFFF5DED6),
    onSurfaceVariant = Color(0xFF53433E),
    outline = Color(0xFF85736D),
    outlineVariant = Color(0xFFD8C2BA),
    inverseSurface = Color(0xFF392E2B),
    inverseOnSurface = Color(0xFFFFEDE8),
    inversePrimary = Color(0xFFFFB59A),
    scrim = Color(0xFF000000),
    surfaceTint = Color(0xFFFF6B35),
    surfaceContainerLowest = Color(0xFFFFFFFF),
    surfaceContainerLow = Color(0xFFFFF1ED),
    surfaceContainer = Color(0xFFFFEBE6),
    surfaceContainerHigh = Color(0xFFFFE5DE),
    surfaceContainerHighest = Color(0xFFFFDED6),
)

private val DarkColor = darkColorScheme(
    primary = Color(0xFFFFB59A),
    onPrimary = Color(0xFF5B1A00),
    primaryContainer = Color(0xFFFF6B35),
    onPrimaryContainer = Color(0xFFFFFFFF),
    secondary = Color(0xFFFFAFD1),
    onSecondary = Color(0xFF650039),
    secondaryContainer = Color(0xFFF72585),
    onSecondaryContainer = Color(0xFFFFFFFF),
    tertiary = Color(0xFFD9B9FF),
    onTertiary = Color(0xFF43006D),
    tertiaryContainer = Color(0xFF7209B7),
    onTertiaryContainer = Color(0xFFFFFFFF),
    error = Color(0xFFFFB4AB),
    errorContainer = Color(0xFF93000A),
    onError = Color(0xFF690005),
    onErrorContainer = Color(0xFFFFDAD6),
    background = Color(0xFF12121F),
    onBackground = Color(0xFFF0ECF4),
    surface = Color(0xFF12121F),
    onSurface = Color(0xFFF0ECF4),
    surfaceVariant = Color(0xFF343342),
    onSurfaceVariant = Color(0xFFD0CAD8),
    outline = Color(0xFF9993A2),
    outlineVariant = Color(0xFF494757),
    inverseSurface = Color(0xFFF0ECF4),
    inverseOnSurface = Color(0xFF2F2D3A),
    inversePrimary = Color(0xFFFF6B35),
    scrim = Color(0xFF000000),
    surfaceTint = Color(0xFFFFB59A),
    surfaceContainerLowest = Color(0xFF0C0C16),
    surfaceContainerLow = Color(0xFF191826),
    surfaceContainer = Color(0xFF1D1C2A),
    surfaceContainerHigh = Color(0xFF282735),
    surfaceContainerHighest = Color(0xFF333240),
)
"""

    text = replace_regex_required(
        text,
        schemes_pattern,
        schemes,
        "Compose color schemes",
    )

    semantic_replacements = {
        "val colorPingRed = Color(0xFFFF0099)":
            "val colorPingRed = Color(0xFFF72585)",

        "val colorConfigType = Color(0xFFf97910)":
            "val colorConfigType = Color(0xFFF72585)",

        "val colorFabActive = Color(0xFFf97910)":
            "val colorFabActive = Color(0xFFFF6B35)",

        "val dividerColorDark = Color(0xFF424242)":
            "val dividerColorDark = Color(0xFF343342)",
    }

    for old, new in semantic_replacements.items():
        if old not in text:
            fail(
                "Could not patch Compose semantic color: "
                f"{old}"
            )

        text = text.replace(old, new, 1)

    write(path, text)

    write(
        root / "V2rayNG/app/src/main/res/values/"
        "parvaz_colors.xml",
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
        / "V2rayNG/app/src/main/java/com/v2ray/ang/"
        "AngApplication.kt"
    )

    text = read(path)

    if "ensureParvazSubscriptions()" not in text:
        text = replace_required(
            text,
            "MMKV.initialize(this)",
            "MMKV.initialize(this)\n"
            "        ensureParvazSubscriptions()",
            "default subscription initialization",
        )

    theme_old = """        // Initialize theme state from MMKV
        ThemeManager.refresh()"""

    theme_new = """        // Use dark mode on first launch, then respect the user's later choice.
        if (!com.v2ray.ang.handler.MmkvManager.decodeSettingsBool("parvaz_theme_initialized")) {
            ThemeManager.setThemeMode("2")
            com.v2ray.ang.handler.MmkvManager.encodeSettings(
                "parvaz_theme_initialized",
                true
            )
        } else {
            ThemeManager.refresh()
        }"""

    if "parvaz_theme_initialized" not in text:
        text = replace_required(
            text,
            theme_old,
            theme_new,
            "default dark mode",
        )

    if "private fun ensureParvazSubscriptions()" not in text:
        defaults = ",\n".join(
            f'            "{name}" to "{url}"'
            for name, url in SUBSCRIPTIONS
        )

        method = f'''

    private fun ensureParvazSubscriptions() {{
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
'''

        position = text.rfind("\n}")

        if position < 0:
            fail(
                "Could not locate AngApplication "
                "class closing brace"
            )

        text = (
            text[:position]
            + method
            + text[position:]
        )

    write(path, text)


def patch_auto_selection(root: Path) -> None:
    view_model_path = (
        root
        / "V2rayNG/app/src/main/java/com/v2ray/ang/"
        "ui/main/MainViewModel.kt"
    )

    view_model = read(view_model_path)

    fields_old = """    @Volatile
    private var testingGroupId: String? = null

    private val initialPageReady"""

    fields_new = """    @Volatile
    private var testingGroupId: String? = null

    private val pendingParvazTestGroups =
        java.util.ArrayDeque<String>()

    private var parvazTestingOnlyTcp: Boolean = false
    private var bestParvazServer: ServersCache? = null
    private var parvazTestWatchdog: Job? = null

    private val initialPageReady"""

    if "pendingParvazTestGroups" not in view_model:
        view_model = replace_required(
            view_model,
            fields_old,
            fields_new,
            "Parvaz test queue fields",
        )

    initialize_old = """                dataSource.initAssets()
                dataSource.syncSubscriptions()"""

    initialize_new = """                dataSource.initAssets()
                dataSource.syncSubscriptions()
                dataSource.updateConfigViaSubAll()
                setupGroupTab(forceRefresh = true).join()
                delay(250L)
                testAllRealPing()"""

    if (
        "dataSource.updateConfigViaSubAll()\n"
        "                setupGroupTab("
        "forceRefresh = true).join()"
        not in view_model
    ):
        view_model = replace_required(
            view_model,
            initialize_old,
            initialize_new,
            "automatic subscription update and startup test",
        )

    testing_pattern = re.compile(
        r"    fun cancelAllPing\(\) \{.*?\n"
        r"    fun testCurrentServerRealPing\(\) \{",
        re.DOTALL,
    )

    testing_replacement = """    fun cancelAllPing() {
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

    fun testAllRealPing(onlyTcp: Boolean = false) {
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

        viewModelScope.launch(ioDispatcher) {
            uiState.value.groups.forEach { group ->
                if (loadGroup(group.id).isNotEmpty()) {
                    pendingParvazTestGroups.addLast(
                        group.id
                    )
                }
            }

            if (pendingParvazTestGroups.isEmpty()) {
                _uiState.update {
                    it.copy(
                        isTesting = false,
                        statusText = disconnectedText
                    )
                }

                return@launch
            }

            startNextParvazGroupTest()
        }

        parvazTestWatchdog = viewModelScope.launch {
            delay(300_000L)

            if (uiState.value.isTesting) {
                cancelAllPing()
            }
        }
    }

    private suspend fun startNextParvazGroupTest() {
        val groupId =
            pendingParvazTestGroups.pollFirst()

        if (groupId == null) {
            finishParvazTesting()
            return
        }

        val servers = loadGroup(groupId)

        testingGroupId = groupId

        dataSource.clearAllTestDelayResults(
            servers.map { it.guid }
        )

        cacheMutex.withLock {
            groupDataCache.remove(groupId)
        }

        dataSource.sendMsg2TestService(
            TestServiceMessage(
                key = AppConfig.MSG_MEASURE_CONFIG_START,
                subscriptionId = groupId,
                serverGuids = emptyList(),
                onlyTcp = parvazTestingOnlyTcp
            )
        )
    }

    fun testCurrentServerRealPing() {"""

    if (
        "private suspend fun "
        "startNextParvazGroupTest()"
        not in view_model
    ):
        view_model = replace_regex_required(
            view_model,
            testing_pattern,
            testing_replacement,
            "multi-group real-delay testing",
        )

    finish_pattern = re.compile(
        r"    private fun onTestsFinished\(\) \{"
        r".*?^\s*\}\s*"
        r"^\s*fun triggerLocateSelectedServer",
        re.DOTALL | re.MULTILINE,
    )

    finish_replacement = """    private fun onTestsFinished() {
        val completedGroupId =
            testingGroupId ?: return

        viewModelScope.launch(ioDispatcher) {
            cacheMutex.withLock {
                groupDataCache.remove(
                    completedGroupId
                )
            }

            val testedServers = loadGroup(
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
                        && groupBest.profile.remarks
                        < previous.profile.remarks
                    )
                ) {
                    bestParvazServer = groupBest

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

        dataSource.setSelectedSubscriptionId(
            server.profile.subscriptionId
        )

        _uiState.update {
            it.copy(
                selectedGroupId =
                    server.profile.subscriptionId,
                selectedGuid = server.guid
            )
        }
    }

    private fun finishParvazTesting() {
        bestParvazServer?.let {
            selectBestParvazServer(it)
        }

        testingGroupId = null
        pendingParvazTestGroups.clear()

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

        reloadAllGroups(
            _uiState.value.groups.map {
                it.id
            }
        )
    }

    fun triggerLocateSelectedServer"""

    if (
        "private fun selectBestParvazServer"
        not in view_model
    ):
        view_model = replace_regex_required(
            view_model,
            finish_pattern,
            finish_replacement,
            "automatic best-server selection",
        )

    write(view_model_path, view_model)

    activity_path = (
        root
        / "V2rayNG/app/src/main/java/com/v2ray/ang/"
        "ui/main/MainActivity.kt"
    )

    activity = read(activity_path)

    fab_pattern = re.compile(
        r"    private fun handleFabAction\(\) \{"
        r".*?^\s*\}\s*"
        r"^\s*private fun handleLayoutTestClick",
        re.DOTALL | re.MULTILINE,
    )

    fab_replacement = """    private fun handleFabAction() {
        if (mainViewModel.uiState.value.isRunning) {
            CoreServiceManager.stopVService(this)
            return
        }

        lifecycleScope.launch {
            if (
                !mainViewModel
                    .uiState
                    .value
                    .isTesting
            ) {
                mainViewModel.testAllRealPing()
            }

            val testCompleted =
                kotlinx.coroutines.withTimeoutOrNull(
                    300_000L
                ) {
                    while (
                        mainViewModel
                            .uiState
                            .value
                            .isTesting
                    ) {
                        kotlinx.coroutines.delay(
                            250L
                        )
                    }

                    true
                } ?: false

            if (!testCompleted) {
                mainViewModel.cancelAllPing()
            }

            if (SettingsManager.isVpnMode()) {
                val intent =
                    VpnService.prepare(
                        this@MainActivity
                    )

                if (intent == null) {
                    startV2Ray()
                } else {
                    requestVpnPermission.launch(
                        intent
                    )
                }
            } else {
                startV2Ray()
            }
        }
    }

    private fun handleLayoutTestClick"""

    if (
        "kotlinx.coroutines.withTimeoutOrNull("
        not in activity
    ):
        activity = replace_regex_required(
            activity,
            fab_pattern,
            fab_replacement,
            "Connect button automation",
        )

    write(activity_path, activity)


def generate_icons(root: Path) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError as error:
        raise RuntimeError(
            "Pillow is required to generate "
            "Parvaz launcher icons"
        ) from error

    res = root / "V2rayNG/app/src/main/res"

    sizes = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    def lerp(
        first: int,
        second: int,
        amount: float,
    ) -> int:
        return round(
            first
            + (second - first) * amount
        )

    start = (255, 107, 53)
    end = (114, 9, 183)

    for folder, size in sizes.items():
        image = Image.new(
            "RGBA",
            (size, size),
            (18, 18, 31, 255),
        )

        draw = ImageDraw.Draw(
            image,
            "RGBA",
        )

        radius = max(
            4,
            size // 5,
        )

        draw.rounded_rectangle(
            (0, 0, size - 1, size - 1),
            radius=radius,
            fill=(18, 18, 31, 255),
        )

        segments = max(
            20,
            size // 2,
        )

        for index in range(segments):
            amount0 = index / segments
            amount1 = (index + 1) / segments

            color = tuple(
                lerp(
                    start[channel],
                    end[channel],
                    amount0,
                )
                for channel in range(3)
            ) + (255,)

            x0 = size * (
                0.18 + 0.56 * amount0
            )

            x1 = size * (
                0.18 + 0.56 * amount1
            )

            top0 = size * (
                0.63
                - 0.43
                * (amount0 ** 0.72)
            )

            top1 = size * (
                0.63
                - 0.43
                * (amount1 ** 0.72)
            )

            bottom0 = size * (
                0.70
                - 0.17 * amount0
            )

            bottom1 = size * (
                0.70
                - 0.17 * amount1
            )

            draw.polygon(
                [
                    (x0, top0),
                    (x1, top1),
                    (x1, bottom1),
                    (x0, bottom0),
                ],
                fill=color,
            )

        width = max(
            2,
            size // 18,
        )

        draw.line(
            (
                size * 0.32,
                size * 0.66,
                size * 0.72,
                size * 0.34,
            ),
            fill=(255, 255, 255, 220),
            width=width,
        )

        speed_color = (
            247,
            37,
            133,
            230,
        )

        for offset, length in (
            (0.0, 0.31),
            (0.10, 0.25),
            (0.20, 0.19),
        ):
            y = size * (
                0.71 + offset
            )

            draw.line(
                (
                    size * 0.15,
                    y,
                    size * (
                        0.15 + length
                    ),
                    y,
                ),
                fill=speed_color,
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
            target / "ic_launcher.png",
            optimize=True,
        )

        round_image = Image.new(
            "RGBA",
            (size, size),
            (0, 0, 0, 0),
        )

        mask = Image.new(
            "L",
            (size, size),
            0,
        )

        ImageDraw.Draw(mask).ellipse(
            (0, 0, size - 1, size - 1),
            fill=255,
        )

        round_image.paste(
            image,
            (0, 0),
            mask,
        )

        round_image.save(
            target / "ic_launcher_round.png",
            optimize=True,
        )

    drawable = res / "drawable"
    drawable.mkdir(
        parents=True,
        exist_ok=True,
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

    adaptive_folder = (
        res / "mipmap-anydpi-v26"
    )

    adaptive_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    for name in (
        "ic_launcher.xml",
        "ic_launcher_round.xml",
    ):
        write(
            adaptive_folder / name,
            """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_parvaz_background" />
    <foreground android:drawable="@drawable/ic_parvaz_foreground" />
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

    strings = read(
        root
        / "V2rayNG/app/src/main/res/"
        "values/strings.xml"
    )

    if f">{APP_NAME}</string>" not in strings:
        fail(
            "app name validation failed"
        )

    theme = read(
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/compose/Theme.kt"
    )

    if (
        "background = Color(0xFF12121F)"
        not in theme
        or
        "primaryContainer = "
        "Color(0xFFFF6B35)"
        not in theme
    ):
        fail(
            "Compose theme validation failed"
        )

    application = read(
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/AngApplication.kt"
    )

    for _, url in SUBSCRIPTIONS:
        if url not in application:
            fail(
                "Subscription validation failed: "
                f"{url}"
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
            "automatic selection "
            "validation failed"
        )

    activity = read(
        root
        / "V2rayNG/app/src/main/java/"
        "com/v2ray/ang/ui/main/"
        "MainActivity.kt"
    )

    if (
        "kotlinx.coroutines.withTimeoutOrNull("
        not in activity
    ):
        fail(
            "Connect automation "
            "validation failed"
        )

    if (
        "CoreServiceManager.stopVService(this)"
        not in activity
    ):
        fail(
            "Stop service automation "
            "validation failed"
        )


def main(argv: Iterable[str]) -> int:
    arguments = list(argv)

    if len(arguments) != 2:
        print(
            "Usage: "
            f"{arguments[0]} "
            "PATH_TO_V2RAYNG_CHECKOUT",
            file=sys.stderr,
        )

        return 2

    root = Path(
        arguments[1]
    ).resolve()

    if not (
        root / "V2rayNG"
    ).is_dir():
        fail(
            f"Not a v2rayNG checkout: {root}"
        )

    patch_gradle(root)
    patch_strings(root)
    patch_compose_theme(root)
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
            main(sys.argv)
        )
    except Exception as error:
        print(
            f"ERROR: {error}",
            file=sys.stderr,
        )

        raise
