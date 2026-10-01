#!/usr/bin/env ruby

require "yaml"

ROOT = File.expand_path("..", __dir__)
MAP_PATH = File.join(ROOT, "data", "knowledge-map.yml")

data = YAML.safe_load(File.read(MAP_PATH), aliases: false)
errors = []

errors << "schema_version must be 2" unless data["schema_version"] == 2

nodes = data.fetch("nodes", [])
edges = data.fetch("edges", [])
ids = nodes.map { |node| node["id"] }

duplicates = ids.group_by(&:itself).select { |_id, values| values.length > 1 }.keys
errors << "duplicate node ids: #{duplicates.join(', ')}" unless duplicates.empty?

allowed_types = data.fetch("node_types", [])
allowed_stages = data.fetch("stages", [])
allowed_statuses = data.fetch("statuses", [])
allowed_relations = data.fetch("relations", [])

nodes.each do |node|
  id = node["id"] || "<missing id>"
  errors << "#{id}: missing title" if node["title"].to_s.strip.empty?
  errors << "#{id}: invalid type #{node['type']}" unless allowed_types.include?(node["type"])
  errors << "#{id}: invalid stage #{node['stage']}" unless allowed_stages.include?(node["stage"])
  errors << "#{id}: invalid status #{node['status']}" unless allowed_statuses.include?(node["status"])
  errors << "#{id}: confidence must be low, medium, or high" unless %w[low medium high].include?(node["confidence"])

  next unless node["guide"]

  guide_path = File.join(ROOT, node["guide"])
  errors << "#{id}: guide does not exist: #{node['guide']}" unless File.file?(guide_path)
end

minimum = data.dig("learning_rules", "edge_weight", "minimum")
maximum = data.dig("learning_rules", "edge_weight", "maximum")

edges.each_with_index do |edge, index|
  label = "edge #{index + 1} (#{edge['from']} -> #{edge['to']})"
  errors << "#{label}: missing source node" unless ids.include?(edge["from"])
  errors << "#{label}: missing target node" unless ids.include?(edge["to"])
  errors << "#{label}: invalid relation #{edge['relation']}" unless allowed_relations.include?(edge["relation"])

  weight = edge["weight"]
  errors << "#{label}: weight must be numeric" unless weight.is_a?(Numeric)
  if weight.is_a?(Numeric) && (weight < minimum || weight > maximum)
    errors << "#{label}: weight #{weight} outside #{minimum}..#{maximum}"
  end
  errors << "#{label}: missing weight_basis" if edge["weight_basis"].to_s.empty?
end

if errors.empty?
  puts "Knowledge map valid: #{nodes.length} nodes, #{edges.length} edges"
  exit 0
end

warn errors.join("\n")
exit 1
