async (page) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const folders = [
    "1.1 环境配置",
    "1.2 C语言入门",
    "1.3 单片机初步认识",
    "1.4 电机与基础控制",
    "1.5 PID与闭环控制",
    "1.6 Git与AI工具使用",
    "1.7 入队综合作业",
  ];
  const errors = [];
  const results = [];
  const onConsole = (message) => {
    if (message.type() === "error") errors.push(message.text());
  };
  const onPageError = (error) => errors.push(`pageerror: ${error.message}`);
  page.on("console", onConsole);
  page.on("pageerror", onPageError);

  for (const folder of folders) {
    const url =
      "http://127.0.0.1:8765/" +
      encodeURIComponent("入队前培训") +
      "/" +
      encodeURIComponent(folder) +
      "/" +
      encodeURIComponent("演示文档.html");
    await page.goto(url, { waitUntil: "load" });
    const count = await page.locator(".slide").count();
    const overflow = [];
    for (let index = 0; index < count; index += 1) {
      await page.evaluate((value) => go(value), index);
      await page.waitForTimeout(25);
      const metrics = await page.locator(".slide.active").evaluate(
        (element, value) => ({
          index: value,
          scrollWidth: element.scrollWidth,
          clientWidth: element.clientWidth,
          scrollHeight: element.scrollHeight,
          clientHeight: element.clientHeight,
        }),
        index,
      );
      if (
        metrics.scrollWidth > metrics.clientWidth + 2 ||
        metrics.scrollHeight > metrics.clientHeight + 2
      ) {
        overflow.push(metrics);
      }
    }
    results.push({ folder, count, overflow });
  }

  const assignmentUrl =
    "http://127.0.0.1:8765/" +
    encodeURIComponent("入队前培训") +
    "/" +
    encodeURIComponent("1.7 入队综合作业") +
    "/" +
    encodeURIComponent("演示文档.html");
  await page.goto(assignmentUrl, { waitUntil: "load" });
  await page.evaluate(() =>
    go([...document.querySelectorAll(".slide")].findIndex((slide) => slide.querySelector("#modeNext"))),
  );
  await page.locator("#modeNext").click();
  await page.locator("#modeNext").click();
  const modeText = await page.locator("#modeText").textContent();

  await page.evaluate(() =>
    go([...document.querySelectorAll(".slide")].findIndex((slide) => slide.querySelector("#pidReset"))),
  );
  await page.locator("#taskKp").evaluate((input) => {
    input.value = "1.20";
    input.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.locator("#pidReset").click();
  await page.waitForTimeout(150);
  const kpText = await page.locator("#taskKpV").textContent();

  page.off("console", onConsole);
  page.off("pageerror", onPageError);
  return { results, errors, modeText, kpText };
}
