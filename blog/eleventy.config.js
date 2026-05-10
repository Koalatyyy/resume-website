module.exports = function (eleventyConfig) {
  eleventyConfig.addFilter("readableDate", (date) =>
    new Date(date).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
  );
  eleventyConfig.addFilter("htmlDateString", (date) =>
    new Date(date).toISOString().split("T")[0]
  );
  eleventyConfig.addFilter("readingTime", (content) => {
    const words = content.replace(/<[^>]+>/g, "").split(/\s+/).filter(Boolean).length;
    return Math.max(1, Math.round(words / 200));
  });
  // Pass through shared assets from root
  eleventyConfig.addPassthroughCopy({ "../style.css": "style.css" });
  eleventyConfig.addPassthroughCopy({ "../fonts": "fonts" });
  eleventyConfig.addPassthroughCopy({ "src/htaccess": ".htaccess" });

  // Sort posts newest first
  eleventyConfig.addCollection("posts", function (collectionApi) {
    return collectionApi
      .getFilteredByGlob("./src/posts/*.md")
      .sort((a, b) => b.date - a.date);
  });

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
    },
    pathPrefix: "/blog/",
  };
};
